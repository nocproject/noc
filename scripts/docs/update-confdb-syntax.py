# ---------------------------------------------------------------------
# Update ConfDB syntax documentation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import NoReturn

# NOC modules
from noc.core.confdb.syntax.base import SYNTAX
from noc.core.confdb.syntax.defs import SyntaxDef

CONFDB_DOC = Path("docs", "confdb-reference")
DOC = CONFDB_DOC / "syntax.md"
START_MARKER = "<!-- SYNTAX START -->"
END_MARKER = "<!-- SYNTAX END -->"
INDENT = " "
CLS_TOKEN = "t"
CLS_NAME = "i"
CLS_MULTI = "m"
CLS_NODE = "n"
CLS_CHILDREN = "c"
CLS_COLAPSED = "x"
CLS_DOC = "d"
rx_tree = re.compile(f"{START_MARKER}(.*?){END_MARKER}", re.MULTILINE | re.DOTALL)
rx_anchor = re.compile(r"^#+.+?{ #(\S+) }\s*$")


def die(msg: str) -> NoReturn:
    print(msg)
    sys.exit(1)


def iter_anchors() -> Iterable[str]:
    """Iterate over all defined anchors."""
    for file_path in CONFDB_DOC.glob("syntax-*.md"):
        prefix = str(file_path.name)[7:-3]
        for line in file_path.read_text().splitlines():
            for match in rx_anchor.finditer(line):
                anchor = match.group(1)
                if not anchor.startswith(prefix):
                    msg = f"{file_path}: invalid anchor {anchor}"
                    raise ValueError(msg)
                yield anchor


def get_syntax_tree() -> str:
    def iter_node(node: SyntaxDef, level: int, path: list[str]) -> Iterable[str]:
        def get_span(node: SyntaxDef) -> str:
            classes: list[str] = []
            if node.name:
                label = node.name
                classes.append(CLS_NAME)
            elif node.token:
                label = node.token
                classes.append(CLS_TOKEN)
            else:
                label = "ANY"
                classes.append(CLS_NAME)
            if node.multi:
                classes.append(CLS_MULTI)
            if classes:
                return f'<span class="{" ".join(classes)}">{label}</span>'
            return f"<span>{label}<span>"

        def get_doc_tag(path: list[str]) -> str:
            anchor = "-".join(path)
            if anchor in anchors:
                seen_anchors.add(anchor)
                return f' <i class="d" data-doc="{anchor}"></i>'
            return ""

        def get_path_item(node: SyntaxDef) -> str:
            if node.name:
                return node.name
            if node.token:
                return node.token
            return "any"

        classes = [CLS_NODE]
        if node.children and (len(node.children) > 1 or node.children[0].children):
            classes.append(CLS_CHILDREN)
            classes.append(CLS_COLAPSED)
        div = f'{INDENT * level}<div class="{" ".join(classes)}">'
        span = get_span(node)
        path = [*path, get_path_item(node)]
        if node.children and len(node.children) == 1 and not node.children[0].children:
            cspan = get_span(node.children[0])
            path = [*path, get_path_item(node.children[0])]
            doc = get_doc_tag(path)
            yield f"{div}{span} {cspan}{doc}</div>"
        elif node.children and len(node.children) == 1:
            yield div
            cspan = get_span(node.children[0])
            path = [*path, get_path_item(node.children[0])]
            doc = get_doc_tag(path)
            yield f"{INDENT * (level + 1)}{span} {cspan}{doc}"
            for child in node.children[0].children:
                yield from iter_node(child, level + 1, path)
            yield f"{INDENT * level}</div>"
        elif node.children:
            doc = get_doc_tag(path)
            yield div
            yield f"{INDENT * (level + 1)}{span}{doc}"
            for child in node.children:
                yield from iter_node(child, level + 1, path)
            yield f"{INDENT * level}</div>"
        else:
            doc = get_doc_tag(path)
            yield f"{div}{span}{doc}</div>"

    def iter_syntax() -> Iterable[str]:
        for c in SYNTAX:
            yield from iter_node(c, 1, [])

    anchors = set(iter_anchors())
    seen_anchors = set()
    r = "\n".join(iter_syntax())
    hanging_anchors = anchors - seen_anchors
    if hanging_anchors:
        die("\n".join(["Invalid anchors in documentations:", *hanging_anchors]))
    return r


def main() -> None:
    tree = get_syntax_tree()
    # read
    data = DOC.read_text()
    # replace
    data = rx_tree.sub(f"{START_MARKER}\n{tree}\n{END_MARKER}", data)
    # write
    DOC.write_text(data)
    print(f"Written {DOC}")


if __name__ == "__main__":
    main()
