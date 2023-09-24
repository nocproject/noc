# ---------------------------------------------------------------------
# Generate connection-types-reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import re
import json
from dataclasses import dataclass
from typing import Optional, List, Iterable, DefaultDict, Tuple, Dict
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

BUCKET_DEPTH = 1
COLLECTION_ROOT = Path("collections", "inv.connectiontypes")
DOCS = Path("docs")
BOOK = Path("connection-types-reference")
TEMPLATE = """# {{ title }}

| Connection Type | Description  | Genders | Compatibility Groups |
| --- | --- | --- |  --- |
{% for item in items -%}
| <a id="{{ item.md_anchor }}"></a>{{ item.md_name }} | {{ item.description }} | `{{ item.genders }}` | {% if item.c_group -%}
{%- for g in item.c_group -%}{{ g }}{% if not loop.last %}, {% endif %}
{%- endfor -%}
{%- endif %} |
{% endfor %}
"""

VALID_GENDERS = {"m", "f", "s", "ss", "mf", "mff", "mmf"}
PEER_GENDERS = {
    "m": {"f"},
    "f": {"m"},
    "s": {"s"},
    "ss": {"s", "ss"},
    "mf": {"m", "f", "mf"},
    "mff": {"f"},
    "mmf": {"m"},
}
rx_md_anchor = re.compile(r"[ _\|\(\)/]+")


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

    def peer_types(self, cgroup: str, cgroups: Dict[str, List["Data"]]) -> List["Data"]:
        items = cgroups.get(cgroup) or []
        return [x for x in items if x.genders in PEER_GENDERS[self.genders]]

    @property
    def md_name(self) -> str:
        """
        Markdown-quoted name
        """
        return self.name.replace("|", "\\|")

    @property
    def md_anchor(self) -> str:
        return rx_md_anchor.sub("-", self.name.lower())

    @property
    def bucket(self) -> Tuple[str, ...]:
        return tuple(islice((x.strip() for x in self.name.split("|", 1)), 0, BUCKET_DEPTH))

    def link_from(self, src: "Data") -> str:
        """
        Generate MD link from source to self.

        Args:
            src: Source item (page)
        """
        dst_bucket = self.bucket
        src_bucket = src.bucket
        anchor = f"#{self.md_anchor}"
        if src_bucket == dst_bucket:
            return anchor
        # Calculate common path
        common = 0
        for x, y in zip(src_bucket, dst_bucket):
            if x == y:
                common += 1
            else:
                break
        # Build link
        link = []
        up = len(src_bucket) - common
        if up > 0:
            link += [".."] * up
        link += list(bucket_path(dst_bucket[common:]).parts)
        return "/".join(link) + anchor


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


def get_buckets() -> DefaultDict[Tuple[str, ...], List[Data]]:
    buckets: DefaultDict[Tuple[str, ...], List[Data]] = defaultdict(list)
    for data in iter_data():
        buckets[data.bucket].append(data)
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


rx_split_alnum = re.compile(r"(\d+|[^0-9]+)")


def _iter_split_alnum(s: str) -> Iterable[str]:
    """
    Iterator yielding alphabetic and numeric sections if string

    :param s:
    :return:
    """
    for match in rx_split_alnum.finditer(s):
        yield match.group(0)


def alnum_key(d: Data) -> str:
    """
    Comparable alpha-numeric key
    """

    def maybe_formatted_int(v: str) -> str:
        try:
            return "%012d" % int(v)
        except ValueError:
            return v

    return "".join(maybe_formatted_int(x) for x in _iter_split_alnum(d.name))


def main():
    """
    Generate Connection Types Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Load buckets
    buckets = get_buckets()
    # Fill cgroups
    cgroups: DefaultDict[str, List[Data]] = defaultdict(list)
    for items in buckets.values():
        for item in items:
            if item.c_group:
                for g in item.c_group:
                    if g:
                        cgroups[g].append(item)
    for g in cgroups:
        cgroups[g] = list(sorted(cgroups[g]))
    # Generate navigation and content
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = Path("index.md")
    for bucket in sorted(buckets):
        rel_path = bucket_path(bucket)
        nav[bucket] = rel_path
        items = list(sorted(buckets[bucket], key=alnum_key))
        out = BOOK / rel_path
        logging.debug("Rendering %s (%d items)", out, len(items))
        # with mkdocs_gen_files.open(out, "w") as fp:
        with open(DOCS / out, "w") as fp:
            title = " | ".join(bucket)
            fp.write(tpl.render(items=items, cgroups=cgroups, title=title))
    # Write navigation
    summary_path = BOOK / "__SUMMARY__"
    # with mkdocs_gen_files.open(summary_path, "w") as fp:
    with open(DOCS / summary_path, "w") as fp:
        fp.writelines(nav.build_literate_nav())


# Execute
if __name__ == "__main__":
    main()
