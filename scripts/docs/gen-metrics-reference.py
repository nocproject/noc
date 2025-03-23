# ---------------------------------------------------------------------
# Generate connection-types-reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import re
import json
import operator
from dataclasses import dataclass
from typing import List, Iterable, Dict, Any
import logging
from pathlib import Path

# Third-party modules
import mkdocs_gen_files
import jinja2

# @todo: Arbitrary ToC depth
# @todo: en/ru

logger = logging.getLogger("mkdocs")

SCOPE_COLLECTION_ROOT = Path("collections", "pm.metricscopes")
TYPE_COLLECTION_ROOT = Path("collections", "pm.metrictypes")

DOCS = Path("docs")
BOOK = Path("metrics-reference")
TEMPLATE = """# {{ scope.name }}

{{ scope.description }}

## Table Structure
The `{{ scope.name }}` metric scope is stored
in the `{{ scope.table_name }}` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
{%- for item in scope.key_fields %}
| {{ item.field_name }} | {{ item.model }} |
{%- endfor %}

{% if scope.labels %}
Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
{%- for item in scope.labels %}
| `{{ item.label }}` | {{ item.view_column }} | {{ item.store_column }} |
{%- endfor %}
{% endif %}

Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
{%- for metric in scope.metrics %}
| <a id="{{ metric.md_anchor }}"></a>{{ metric.field_name }} | {{ metric.field_type }} | {{ metric.md_name }} | {{ metric.description }} | {{ metric.measure }} | {{ metric.units }} | {{ metric.scale }} |
{%- endfor %}
"""


rx_md_anchor = re.compile(r"[ _\|\(\)/]+")


@dataclass(order=True)
class Metric(object):
    scope: str
    name: str
    field_name: str
    field_type: str
    description: str
    measure: str
    units: str
    scale: str

    @classmethod
    def read(cls, path: Path) -> "Metric":
        with open(path) as fp:
            data = json.load(fp)
        return Metric(
            scope=data["scope__name"],
            name=data["name"],
            field_name=data["field_name"],
            field_type=data["field_type"],
            description=data["description"],
            measure=data["measure"],
            units=data["units__code"],
            scale=data["scale__code"],
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


@dataclass
class KeyField(object):
    field_name: str
    model: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "KeyField":
        return KeyField(field_name=data["field_name"], model=data["model"])


@dataclass
class Label(object):
    label: str
    view_column: str
    store_column: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Label":
        return Label(
            label=data["label"],
            view_column=data.get("view_column", ""),
            store_column=data.get("store_column", ""),
        )


@dataclass(order=True)
class Data(object):
    """
    Collections data.

    Attributes:
        name: Connection Type name
        description: List of descriptions
        c_groups: List of compatibility group names
        genders: Available genders
    """

    name: str
    description: str
    table_name: str
    key_fields: List[KeyField]
    labels: List[Label]
    metrics: List[Metric]

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
            description=data["description"],
            table_name=data["table_name"],
            metrics=[],
            key_fields=[KeyField.from_json(d) for d in data["key_fields"]],
            labels=[Label.from_json(d) for d in data.get("labels", [])],
        )


def iter_data() -> Iterable[Data]:
    """
    Iterate collection data.

    Returns:
        Yields Data structures
    """
    logger.info("Reading collections")
    n = 0
    t = time.time()
    for path in SCOPE_COLLECTION_ROOT.rglob("*.json"):
        yield Data.read(path)
        n += 1
    dt = time.time() - t
    logger.info("%d items read in %.3fs", n, dt)


def canonical_name(s: str) -> str:
    """
    Convert name to canonical one.
    """
    return s.replace(" | ", "-").replace(" ", "-").lower()


def main():
    """
    Generate Connection Types Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Load scopes
    scopes = {ms.name: ms for ms in iter_data()}
    # Load types
    for path in TYPE_COLLECTION_ROOT.rglob("*.json"):
        mt = Metric.read(path)
        scopes[mt.scope].metrics.append(mt)
    # Generate navigation and content
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = Path("index.md")
    for scope in sorted(scopes.values()):
        scope.metrics = list(sorted(scope.metrics, key=operator.attrgetter("field_name")))
        rel_path = f"{canonical_name(scope.name)}.md"
        nav[scope.name] = rel_path
        out = BOOK / rel_path
        logging.debug("Rendering %s", out)
        # with mkdocs_gen_files.open(out, "w") as fp:
        with open(DOCS / out, "w") as fp:
            fp.write(tpl.render(scope=scope))
    # Write navigation
    summary_path = BOOK / "SUMMARY.md"
    # with mkdocs_gen_files.open(summary_path, "w") as fp:
    with open(DOCS / summary_path, "w") as fp:
        fp.writelines(nav.build_literate_nav())


# Execute
if __name__ == "__main__":
    main()
