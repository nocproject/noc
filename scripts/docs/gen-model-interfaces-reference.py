# ---------------------------------------------------------------------
# Generate model interfaces reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import re
import json
from dataclasses import dataclass
from typing import Iterable, Dict, Any, List
import logging
from pathlib import Path
import os

# Third-party modules
import jinja2
import mkdocs_gen_files

# @todo: Arbitrary ToC depth
# @todo: en/ru

logger = logging.getLogger("mkdocs")

COLLECTION_ROOT = Path("collections", "inv.modelinterfaces")
DOCS = Path("docs")
BOOK = Path("model-interfaces-reference")
TEMPLATE = """<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
{% for item in items -%}
| `{{ item.md_name }}` | {{ item.type }} | {{ item.description }} | {{ bq(item.required) }} | {{ bq(item.is_const) }} |
{% endfor %}
<!-- table end -->
"""


rx_md_anchor = re.compile(r"[ _\|\(\)/]+")
rx_table = re.compile(r"<!-- table start -->.*<!-- table end -->", re.MULTILINE | re.DOTALL)


@dataclass(order=True)
class Item(object):
    name: str
    type: str
    description: str
    required: bool
    is_const: bool

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Item":
        """
        Read from JSON.

        Returns:
            Initialized Item structure
        """
        return Item(
            name=data["name"],
            type=data["type"],
            description=data.get("description", ""),
            required=data["required"],
            is_const=data["is_const"],
        )

    @property
    def md_name(self) -> str:
        """
        Markdown-quoted name
        """
        return self.name.replace("|", "\\|")

    @property
    def md_anchor(self) -> str:
        return rx_md_anchor.sub("-", self.name.lower())


@dataclass(order=True)
class Data(object):
    """
    Collections data.

    Attributes:
        name: Connection Type name
        description: List of descriptions
        type: Data Type
    """

    name: str
    items: List[Item]

    @classmethod
    def read(cls, path: Path) -> "Data":
        """
        Read from JSON.

        Args:
            path: File path

        Returns:
            Initialized Data structure
        """
        with open(path) as fp:
            data = json.load(fp)
        return Data(name=data["name"], items=[Item.from_json(x) for x in data["attrs"]])


def iter_data() -> Iterable[Data]:
    """
    Iterate collection data.

    Returns:
        Yields Data structures
    """
    logger.info("Reading collections")
    n = 0
    t = time.time()
    for path in COLLECTION_ROOT.rglob("*.json"):
        yield Data.read(path)
        n += 1
    dt = time.time() - t
    logger.info("%d items read in %.3fs", n, dt)


def has_valid_markup(s: str) -> bool:
    """
    Check if text has valid markup
    """
    return bool(rx_table.search(s))


def main():
    """
    Generate Measurement Units Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Process data
    print("# Processing Model Interfaces")
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = Path("index.md")
    for mi in sorted(iter_data()):
        print(f"## {mi.name}")
        # Read current file
        path = DOCS / BOOK / f"{mi.name}.md"
        if not os.path.exists(path):
            print(f"Missed file: {path}")
            continue
        with open(path) as fp:
            data = fp.read()
        if not has_valid_markup(data):
            msg = f"Cannot find table markup in {path}"
            raise ValueError(msg)
        #
        nav[mi.name] = f"{mi.name}.md"
        #
        table = tpl.render(items=mi.items, bq=bq)
        data = rx_table.sub(table, data)
        # Write
        with open(path, "w") as fp:
            fp.write(data)
    # Write navigation
    summary_path = BOOK / "SUMMARY.md"
    with open(DOCS / summary_path, "w") as fp:
        fp.writelines(nav.build_literate_nav())


def bq(x: bool) -> str:
    """
    Convert boolean to pretty string
    """
    if x:
        return "{{ yes }}"
    return "{{ no }}"


# Execute
if __name__ == "__main__":
    main()
