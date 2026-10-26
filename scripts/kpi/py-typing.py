#!/usr/bin/env python3
# ----------------------------------------------------------------------
# Python typing KPI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Future imports
from __future__ import annotations

# Python modules
import ast
import csv
import sys
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass(slots=True)
class KPI:
    file: Path
    module: str
    cls: str | None
    function: str
    lineno: int
    args_typed: bool
    return_typed: bool
    uses_any: bool

    @property
    def is_typed(self) -> bool:
        return self.args_typed and self.return_typed and not self.uses_any


@dataclass(slots=True)
class KPISummary:
    """
    KPI Summary.

    Attributes:
        total_packages: Total amount of scanned packages.
        total_modules: Total amount of scanned modules.
        total_classes: Total amount of scanned classes.
        total_functions: Total amount of scanned functions.
        typed_modules: Modules with all typed functions.
        typed_classes: Classes with all typed functions.
        typed_functions: Fully typed functions.
        typed_modules_percent: Percentage of typed modules, None - if cannot be calculated.
        typed_classes_percent: Percentage of typed classes, None - if cannot be calculated.
        typed_functions_percent: Percentage of typed functions, None - if cannot be calculated.
    """

    total_packages: int
    total_modules: int
    total_classes: int
    total_functions: int
    typed_packages: int
    typed_modules: int
    typed_classes: int
    typed_functions: int
    typed_packages_percent: float | None
    typed_modules_percent: float | None
    typed_classes_percent: float | None
    typed_functions_percent: float | None

    @classmethod
    def from_rows(cls, rows: Iterable[KPI]) -> KPISummary:
        """Build summary from rows iterator."""

        def ratio(value: int, base: int) -> float | None:
            if base > 1:
                return float(value) * 100.0 / float(base)
            return None

        def iter_packages(mod_name: str) -> Iterable[str]:
            """Iterate all module packages upwards."""
            parts = mod_name.split(".")[:-1]
            while parts:
                yield ".".join(parts)
                parts.pop(-1)

        total_functions = 0
        typed_functions = 0
        package_typing: dict[str, bool] = {}
        module_typing: dict[str, bool] = {}
        class_typing: dict[str, bool] = {}
        for kpi in rows:
            for pkg in iter_packages(kpi.module):
                if pkg not in package_typing:
                    package_typing[pkg] = True
            if kpi.module not in module_typing:
                module_typing[kpi.module] = True
            if kpi.cls:
                cls_name = f"{kpi.module}.{kpi.cls}"
            else:
                cls_name = None
            if cls_name and cls_name not in class_typing:
                class_typing[cls_name] = True
            if kpi.is_typed:
                typed_functions += 1
            else:
                module_typing[kpi.module] = False
                for pkg in iter_packages(kpi.module):
                    package_typing[pkg] = False
                if cls_name:
                    class_typing[cls_name] = False
            total_functions += 1
        total_packages = len(package_typing)
        total_modules = len(module_typing)
        total_classes = len(class_typing)
        typed_packages = sum(1 for v in package_typing.values() if v)
        typed_modules = sum(1 for v in module_typing.values() if v)
        typed_classes = sum(1 for v in class_typing.values() if v)
        return KPISummary(
            total_packages=total_packages,
            total_modules=total_modules,
            total_classes=total_classes,
            total_functions=total_functions,
            typed_packages=typed_packages,
            typed_modules=typed_modules,
            typed_classes=typed_classes,
            typed_functions=typed_functions,
            typed_packages_percent=ratio(typed_packages, total_packages),
            typed_modules_percent=ratio(typed_modules, total_modules),
            typed_classes_percent=ratio(typed_classes, total_classes),
            typed_functions_percent=ratio(typed_functions, total_functions),
        )


class AnyVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.found = False

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "Any":
            self.found = True

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "Any":
            self.found = True
        self.generic_visit(node)


def annotation_uses_any(node: ast.AST | None) -> bool:
    if node is None:
        return False

    visitor = AnyVisitor()
    visitor.visit(node)
    return visitor.found


def args_typed(args: ast.arguments) -> bool:
    skip_first = True

    for arg in args.posonlyargs + args.args:
        if skip_first and arg.arg in {"self", "cls"}:
            skip_first = False
            continue

        skip_first = False

        if arg.annotation is None:
            return False

    for arg in args.kwonlyargs:
        if arg.annotation is None:
            return False

    if args.vararg and args.vararg.annotation is None:
        return False

    return not (args.kwarg and args.kwarg.annotation is None)


def function_uses_any(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
        if annotation_uses_any(arg.annotation):
            return True

    if node.args.vararg:
        if annotation_uses_any(node.args.vararg.annotation):
            return True

    if node.args.kwarg:
        if annotation_uses_any(node.args.kwarg.annotation):
            return True

    return bool(annotation_uses_any(node.returns))


class KPIVisitor:
    """
    Walk only module/class namespace.

    Function bodies are intentionally not traversed,
    therefore nested functions are ignored.
    """

    def __init__(
        self,
        file: Path,
        module: str,
    ) -> None:
        self.file = file
        self.module = module
        self.class_stack: list[str] = []
        self.rows: list[KPI] = []

    def visit(self, node: ast.AST) -> None:
        match node:
            case ast.Module():
                for item in node.body:
                    self.visit(item)

            case ast.ClassDef():
                self.visit_class(node)

            case ast.FunctionDef() | ast.AsyncFunctionDef():
                self.visit_function(node)

            case _:
                pass

    def visit_class(
        self,
        node: ast.ClassDef,
    ) -> None:
        self.class_stack.append(node.name)

        for item in node.body:
            self.visit(item)

        self.class_stack.pop()

    def visit_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        self.rows.append(
            KPI(
                file=self.file,
                module=self.module,
                cls=".".join(self.class_stack),
                function=node.name,
                lineno=node.lineno,
                args_typed=args_typed(node.args),
                return_typed=node.returns is not None,
                uses_any=function_uses_any(node),
            )
        )


def get_module_name(path: Path) -> str:
    """Convert path to module name."""
    parts = path.with_suffix("").parts
    if parts[:2] == ("src", "noc"):
        parts = parts[2:]
    return ".".join(("noc", *parts))


def scan_module(path: Path) -> Iterable[KPI]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

    except SyntaxError as e:
        print(f"WARNING: cannot parse {path}: {e}")
        return ()

    visitor = KPIVisitor(
        file=path,
        module=get_module_name(path),
    )

    visitor.visit(tree)

    return visitor.rows


_ignored_dirs = {
    "ansible",
    "ui",
    "docs",
    "dist",
    "build",
    "docker",
    "examples",
    "var",
}


def can_scan(path: Path) -> bool:
    parts = path.parts

    if parts and parts[0] in _ignored_dirs:
        return False

    for part in parts:
        if part.startswith("."):
            return False

        if part == "__pycache__":
            return False

    return True


def canonical_name(path: Path) -> Path:
    parts = path.parts

    if parts[:2] == ("src", "noc"):
        return path

    return Path("src", "noc", *parts)


def scan_tree() -> Iterable[KPI]:
    root = Path.cwd()
    seen: set[Path] = set()
    for path in sorted(root.rglob("*.py")):
        rel_path = path.relative_to(root)
        if not can_scan(rel_path):
            continue
        canonical_path = canonical_name(rel_path)
        effective_path = canonical_path if canonical_path.exists() else rel_path
        if effective_path in seen:
            continue

        yield from scan_module(effective_path)


def write_csv(
    rows: Iterable[KPI],
    output: TextIO,
) -> None:
    writer = csv.writer(output)

    writer.writerow(
        [
            "file",
            "module",
            "class",
            "function",
            "lineno",
            "args_typed",
            "return_typed",
            "uses_any",
        ]
    )

    with suppress(BrokenPipeError):
        for row in rows:
            writer.writerow(
                [
                    row.file,
                    row.module,
                    row.cls,
                    row.function,
                    row.lineno,
                    "yes" if row.args_typed else "no",
                    "yes" if row.return_typed else "no",
                    "yes" if row.uses_any else "no",
                ]
            )


def dump_summary(rows: Iterable[KPI]):
    def qp(v: float | None) -> str:
        if v is None:
            return "-"
        return f"{v:7.2f}%"

    summary = KPISummary.from_rows(rows)
    print("# Python Typing Summary")
    print("| Name      | Typed  | Total  | %        |")
    print("| --------- | -----: | -----: | -------: |")
    print(
        "| Packages  "
        f"| {summary.typed_packages:-6d} "
        f"| {summary.total_packages:-6d} "
        f"| {qp(summary.typed_packages_percent)} |"
    )
    print(
        "| Modules   "
        f"| {summary.typed_modules:-6d} "
        f"| {summary.total_modules:-6d} "
        f"| {qp(summary.typed_modules_percent)} |"
    )
    print(
        "| Classes   "
        f"| {summary.typed_classes:-6d} "
        f"| {summary.total_classes:-6d} "
        f"| {qp(summary.typed_classes_percent)} |"
    )
    print(
        "| Functions "
        f"| {summary.typed_functions:-6d} "
        f"| {summary.total_functions:-6d} "
        f"| {qp(summary.typed_functions_percent)} |"
    )


def main() -> None:
    if "--summary" in sys.argv:
        dump_summary(scan_tree())
    else:
        write_csv(
            scan_tree(),
            sys.stdout,
        )


if __name__ == "__main__":
    main()
