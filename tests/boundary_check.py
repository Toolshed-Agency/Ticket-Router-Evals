"""Finds code under harness/ that crosses the harness boundary (spec D1, section 5).

harness/ is the general machinery Toolshed copies into client projects, so it must not import the
Ledgerly routers or scoring (router/, evals/), read the Ledgerly data or policy (data/, context/),
or mention Ledgerly at all.

It fails closed: a bare "data" or "context" string counts as a path unless it is plainly used as
a key or compared, because the ways to build a path from it are too many to list (the phase 1
review found eleven the first version missed).
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path

FORBIDDEN_MODULES = ("router", "evals")
FORBIDDEN_DIRS = ("data", "context")
DYNAMIC_IMPORTS = frozenset({"import_module", "__import__"})
KEY_METHODS = frozenset({"get", "pop", "setdefault"})  # x.get("data") reads a key, not a path


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
    # Names that act as importlib.import_module, including aliases such as `import_module as im`.
    importers = set(DYNAMIC_IMPORTS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "importlib":
            importers |= {a.asname or a.name for a in node.names if a.name == "import_module"}

    found: list[Violation] = []
    not_a_path: set[int] = set()  # ids of string constants used as keys or compared
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
            if name is not None and (name in importers or name.endswith(tuple(DYNAMIC_IMPORTS))):
                for arg in [*node.args, *(keyword.value for keyword in node.keywords)]:
                    module = _constant_text(arg)
                    if module is not None and _is_forbidden_module(module):
                        found.append(Violation(path, node.lineno, f"imports {module}"))
            if isinstance(node.func, ast.Attribute) and node.func.attr in KEY_METHODS and node.args:
                not_a_path.add(id(node.args[0]))
        elif isinstance(node, ast.Subscript):
            not_a_path.add(id(node.slice))
        elif isinstance(node, ast.Dict):
            not_a_path.update(id(key) for key in node.keys if key is not None)
        elif isinstance(node, ast.Compare):
            not_a_path.update(id(operand) for operand in (node.left, *node.comparators))
    found += [
        Violation(path, node.lineno, f"reads {node.value!r}")
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (
            (node.value in FORBIDDEN_DIRS and id(node) not in not_a_path)
            or _has_forbidden_segment(node.value)
        )
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


def _constant_text(node: ast.expr) -> str | None:
    """The text of a string constant, or of an f-string made only of constant parts."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and all(
        isinstance(part, ast.Constant) and isinstance(part.value, str) for part in node.values
    ):
        return "".join(str(part.value) for part in node.values if isinstance(part, ast.Constant))
    return None


def _has_forbidden_segment(text: str) -> bool:
    """True for a path string such as "data/x" or "data\\x"; never for a bare word."""
    if "/" not in text and "\\" not in text:
        return False
    return any(segment in FORBIDDEN_DIRS for segment in re.split(r"[/\\]", text))
