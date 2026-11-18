"""Finds code under harness/ that crosses the harness boundary (spec D1, section 5).

harness/ is the general machinery Toolshed copies into client projects, so it must not import the
Ledgerly routers or scoring (router/, evals/), read the Ledgerly data or policy (data/, context/),
or mention Ledgerly at all.
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path

FORBIDDEN_MODULES = ("router", "evals")
FORBIDDEN_DIRS = ("data", "context")
DYNAMIC_IMPORTS = frozenset({"import_module", "__import__"})
PATH_CALLS = frozenset({"Path", "PurePath", "open", "join", "joinpath"})


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    reason: str


def find_violations(root: Path) -> list[Violation]:
    """Every boundary violation in the .py files under root, in file and line order."""
    files = sorted(root.rglob("*.py"))
    if not files:
        # A check with nothing to check must fail, or a renamed folder would pass silently.
        raise ValueError(f"no .py files under {root}")
    violations = [v for path in files for v in _check_file(path)]
    return sorted(violations, key=lambda v: (str(v.path), v.line))


def _check_file(path: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    # Comments are not in the syntax tree, so the name is searched in the raw text.
    found = [
        Violation(path, number, "mentions Ledgerly")
        for number, line in enumerate(text.splitlines(), start=1)
        if "ledgerly" in line.lower()
    ]
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as error:
        return [*found, Violation(path, error.lineno or 0, f"does not parse: {error.msg}")]
    return found + _check_tree(path, tree)


def _check_tree(path: Path, tree: ast.Module) -> list[Violation]:
    found: list[Violation] = []
    used_as_path: set[int] = set()  # ids of bare "data" or "context" constants used as paths
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [
                Violation(path, node.lineno, f"imports {alias.name}")
                for alias in node.names
                if _is_forbidden_module(alias.name)
            ]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module and _is_forbidden_module(node.module):
                found.append(Violation(path, node.lineno, f"imports {node.module}"))
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            for arg in node.args:
                if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    continue
                if name in DYNAMIC_IMPORTS and _is_forbidden_module(arg.value):
                    found.append(Violation(path, node.lineno, f"imports {arg.value}"))
                elif name in PATH_CALLS and arg.value in FORBIDDEN_DIRS:
                    used_as_path.add(id(arg))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            for side in (node.left, node.right):
                if isinstance(side, ast.Constant) and side.value in FORBIDDEN_DIRS:
                    used_as_path.add(id(side))
    found += [
        Violation(path, node.lineno, f"reads {node.value!r}")
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (id(node) in used_as_path or _has_forbidden_segment(node.value))
    ]
    return found


def _is_forbidden_module(name: str) -> bool:
    return name.split(".")[0] in FORBIDDEN_MODULES


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _has_forbidden_segment(text: str) -> bool:
    """True for a path string such as "data/x" or "data\\x"; never for a bare word."""
    if "/" not in text and "\\" not in text:
        return False
    return any(segment in FORBIDDEN_DIRS for segment in re.split(r"[/\\]", text))
