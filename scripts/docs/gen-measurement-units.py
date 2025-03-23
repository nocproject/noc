# ---------------------------------------------------------------------
# Generate measurement units
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import re
import json
from dataclasses import dataclass
from typing import Iterable
import logging
from pathlib import Path

# Third-party modules
import jinja2

# @todo: Arbitrary ToC depth
# @todo: en/ru

logger = logging.getLogger("mkdocs")

COLLECTION_ROOT = Path("collections", "pm.measurementunits")
DOCS = Path("docs")
BOOK = Path("measurement-units-reference", "index.md")
TEMPLATE = """<!-- table start -->
| Name | Description | Label | Dashboard<br>Label |
| ---- | ----------- | ----- | ------------------ |
{% for item in items -%}
| <a id="{{ item.md_anchor }}"></a>{{ item.md_name }} | {{ item.description }} | `{{ item.label }}` | `{{ item.dashboard_label }}` |
{% endfor %}
<!-- table end -->
"""


rx_md_anchor = re.compile(r"[ _\|\(\)/]+")
rx_table = re.compile(r"<!-- table start -->.*<!-- table end -->", re.MULTILINE | re.DOTALL)


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
    description: str
    label: str
    dashboard_label: str

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
        return Data(
            name=data["name"],
            description=data.get("description", ""),
            label=data["label"],
            dashboard_label=data["dashboard_label"],
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


def main():
    """
    Generate Measurement Units Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Load items
    items = list(sorted(iter_data()))
    # Render table
    table = tpl.render(items=items)
    with open(DOCS / BOOK) as fp:
        data = fp.read()
    data = rx_table.sub(table, data)
    # Write
    with open(DOCS / BOOK, "w") as fp:
        fp.write(data)


# Execute
if __name__ == "__main__":
    main()
