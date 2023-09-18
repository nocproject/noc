# ---------------------------------------------------------------------
# Generate connection-types-reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import json
from dataclasses import dataclass
from typing import Optional, List, Iterable, DefaultDict, Tuple
import logging
from collections import defaultdict
from pathlib import Path
from itertools import islice

# Third-party modules
import mkdocs_gen_files
import jinja2

# @todo: Arbitrary ToC depth
# @todo: en/ru

logger = logging.getLogger("mkdocs")

COLLECTION_ROOT = Path("collections", "inv.connectiontypes")
DOCS = Path("docs")
BOOK = Path("connection-types-reference")
TEMPLATE = """# @todo: Header
{% for item in items %}
## {{ item.name }}

{{ item.description }}

Genders
: `{{ item.gender }}` - {% if item.gender == "m" %}only male types, compatible female types are selected via `c_groups`
{% elif item.gender == "f" %}only female types, compatible male types are selected via `c_groups`
{% elif item.gender == "s" %}symmetric, genderless same type connection
{% elif item.gender == "ss" %}symmetric, genderless same type connection. More than two objects may be connected
{% elif item.gender == "mf" %}male and female types
{% elif item.gender == "mmf" %}one or more male may be connected to one female
{% elif item.gender == "mff" %}two or one females may be connected to one male
{% endif %}

{% if item.cgroups %}
CGroups
: {% for g in item.cgroups %}- {{ g }}:

{% for gi in cgroups[gi] %}    - {{ gi.name }}
{% endfor %}
{% endfor %}
{% endif %}
{% endfor %}
"""

VALID_GENDERS = {"m", "f", "s", "ss", "mf", "mff", "mmf"}


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
    c_group: Optional[List[str]]
    genders: str

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
        genders = data["genders"]
        if genders not in VALID_GENDERS:
            msg = f"Invalid gender `{genders}` in file {path}"
            raise ValueError(msg)
        return Data(
            name=data["name"],
            description=data["description"],
            genders=genders,
            c_group=data.get("c_group") or None,
        )


def get_bucket(data: Data, depth: int) -> Tuple[str, ...]:
    """
    Content section.

    Args:
        Maximal level of depth

    Returns:
        Leading parts of name
    """
    return tuple(islice((x.strip() for x in data.name.split("|", 1)), 0, depth))


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


def get_buckets(depth: int) -> DefaultDict[Tuple[str, ...], List[Data]]:
    buckets: DefaultDict[Tuple[str, ...], List[Data]] = defaultdict(list)
    for data in iter_data():
        buckets[get_bucket(data, depth)].append(data)
    return buckets


def canonical_name(s: str) -> str:
    """
    Convert name to canonical one.
    """
    return s.replace(" | ", "-").replace(" ", "-").lower()


def bucket_path(s: Tuple[str, ...]) -> Path:
    """
    Convert bucket tuple to .md path
    """
    return Path(*tuple(canonical_name(x) for x in s)).with_suffix(".md")


def main():
    """
    Generate Connection Types Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Load buckets
    buckets = get_buckets(1)
    # Fill cgroups
    cgroups: DefaultDict[str, List[Data]] = defaultdict(list)
    for items in buckets.values():
        for item in items:
            if item.c_group:
                for g in item.c_group:
                    cgroups[g].append(item)
    for g in cgroups:
        cgroups[g] = list(sorted(cgroups[g]))
    # Generate navigation and content
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = Path("index.md")
    for bucket in sorted(buckets):
        rel_path = bucket_path(bucket)
        nav[bucket] = rel_path
        items = list(sorted(buckets[bucket]))
        out = BOOK / rel_path
        logging.debug("Rendering %s (%d items)", out, len(items))
        with mkdocs_gen_files.open(out, "w") as fp:
            fp.write(tpl.render(items=items, cgroups=sorted(cgroups)))
    # Write navigation
    summary_path = BOOK / "SUMMARY.md"
    with mkdocs_gen_files.open(summary_path, "w") as fp:
        fp.writelines(nav.build_literate_nav())


# Execute
main()
