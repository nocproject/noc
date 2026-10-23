# ----------------------------------------------------------------------
# Report Band Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Any
from collections.abc import Iterable

# Third-party modules
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
from noc.core.reporter.types import BandOrientation, ROOT_BAND, ReportBand


@dataclass
class DataSet:
    name: str
    data: pl.DataFrame
    rows: list[dict[str, Any]] | None = None
    query: str | None = None
    transpose: bool = False
    transpose_columns: list[str] | None = None


class Band:
    """
    Report Data for Band. Contains data, rows and format options
    """

    __slots__ = (
        "children_bands",
        "data",
        "datasets",
        "format",
        "name",
        "orientation",
        "parent",
        "report_field_format",
        "title_template",
    )

    def __init__(
        self,
        name: str,
        parent: Optional["Band"] = None,
        orientation: BandOrientation = BandOrientation.HORIZONTAL,
        data: dict[str, Any] | None = None,
    ):
        self.name = name
        self.parent = parent
        self.children_bands: list[Band] = []
        self.orientation = orientation
        self.datasets: dict[str, DataSet] = {}
        self.data: dict[str, Any] = data or {}
        # self.rows: Optional[DataFrame] = rows
        # self.format: Optional[BandFormat] = None
        # self.report_field_format: Dict[str, ReportField] = {}

    def __str__(self) -> str:
        return f'Band "{self.name}"'

    def __repr__(self) -> str:
        return (
            f'Band "{self.name}" (parent: {self.parent}, '
            f"children_bands: {len(self.children_bands)}, "
            f"datasets: {len(self.datasets)}, "
            f"data: {len(self.data)})"
        )

    def diagram(self, max_width=100, panel_width=60, level_offset=4) -> str:
        """Generate pretty textual diagram of band and all its children"""

        def get_panel(data: list[str], offset: int, width: int) -> str:
            offset_str = " " * offset
            width_wob = width - 2
            top_line = f"{offset_str}┌{'─' * width_wob}┐\n"
            bot_line = f"{offset_str}└{'─' * width_wob}┘\n"
            data_lines = []
            for row in data:
                row = row.replace("\n", "")
                row = row[: width_wob - 1] + "…" if len(row) > width_wob else row.ljust(width_wob)
                line = f"{offset_str}│{row}│\n"
                data_lines.append(line)
            data_lines = "".join(data_lines)
            return "".join((top_line, data_lines, bot_line))

        def get_band_instance_image(band: Band, offset: int) -> str:
            """Image for band only (without children bands)"""

            def format_dataframe(df: pl.DataFrame | None) -> str:
                if df is None:
                    return "None"
                return f"DataFrame (rows: {df.shape[0]}, cols: {df.shape[1]})"

            data = [
                f"Band name: {band.name}",
                f"==========={'=' * len(band.name)}",
                f"orientation: {band.orientation}",
                "data",
            ]
            for k, v in band.data.items():
                data.append(f"  {k}: {v}")
            data.append("datasets")
            for k, v in band.datasets.items():
                data.append(f"  {k}: Dataset {v.name}")
                data.append(f"    data: {format_dataframe(v.data)}")
                if v.data is not None:
                    data.append(f'    > band.datasets["{k}"].data.columns')
                data.append(f"    rows: {v.rows}")
                data.append(f"    query: {v.query}")
                data.append(f"    transpose: {v.transpose}")
                data.append(f"    transpose_columns: {v.transpose_columns}")
            return get_panel(data, offset, panel_width)

        def get_band_image(band: Band, offset: int) -> str:
            """Image for band with children bands (recursive)"""
            band_image = get_band_instance_image(band, offset)
            children_image = "".join(
                get_band_instance_image(b, offset + level_offset) for b in band.children_bands
            )
            return "\n\n".join((band_image, children_image))

        def get_cropped_band_image(band: Band, offset: int) -> str:
            def crop_string(value: str) -> str:
                return value[: max_width - 1] + ">" if len(value) > max_width else value

            lines = get_band_image(band, offset).split("\n")
            return "\n".join(crop_string(row) for row in lines)

        return get_cropped_band_image(self, 0)

    def print_diagram(self):
        print(self.diagram())

    @property
    def is_root(self) -> bool:
        """Return True if Root Band"""
        return not self.parent or self.name == ROOT_BAND

    @property
    def has_children(self) -> bool:
        return bool(self.children_bands)

    @property
    def has_rows(self) -> bool:
        if not self.datasets:
            return False
        r = self.get_rows()
        return any(not x.is_empty() for x in r)

    @property
    def full_name(self):
        """Calculate full BandName - <rb>.<b1>.<b2>"""
        return ".".join(b.name for b in self.get_path()[1:])

    def get_columns(self) -> list[str]:
        r = self.get_rows()
        if not r and not self.data:
            return []
        if self.data:
            return list(self.data)
        return r[0].columns

    def add_children(self, bands: list["Band"]):
        """
        Add children Band
        Attrs:
            bands: List of Bands
        """
        for b in bands:
            self.add_child(b)

    def add_child(self, band: "Band"):
        """Add child band"""
        band.parent = self
        self.children_bands.append(band)

    def get_path(self) -> list["Band"]:
        """Getting band path"""
        if self.parent:
            return [*self.parent.get_path(), self]
        return [self]

    def get_rows(self) -> list[pl.DataFrame]:
        """Getting rows for Band"""
        if not self.datasets:
            return []
        ctx = {}
        sql = pl.SQLContext()
        # do get_sql
        # Create SQL context
        r = []
        for b in self.get_path():
            ctx.update(b.data)
            if b.name not in b.datasets:
                continue
            ds = b.datasets[b.name]
            if ds.rows:
                r.append(pl.DataFrame(ds.rows))
                continue
            if ds.query and ds.data is None:
                rows = sql.execute(Jinja2Template(ds.query).render(ctx), eager=True)
            elif ds.query and ds.data is not None:
                try:
                    rows = ds.data.sql(Jinja2Template(ds.query).render(ctx))
                except pl.exceptions.ColumnNotFoundError:
                    continue
            elif not ds.query and ds.data is not None:
                rows = ds.data
            else:
                continue
            if ds.transpose and not ds.transpose_columns:
                # rows = rows.transpose(include_header=True)
                rows = rows.transpose(include_header=True)
            elif ds.transpose and ds.transpose_columns:
                rows = rows.transpose(
                    include_header=True,
                    header_name=ds.transpose_columns[0],
                    column_names=ds.transpose_columns[1:],
                )
            if b.name == self.name:
                r.append(rows)
            else:
                sql.register(b.name, rows.lazy())
        return r

    def iter_rows(self) -> Iterable[dict[str, Any]]:
        """iterate row dataset"""
        for r in self.get_rows():
            yield from r.to_dicts()

    def iter_data_rows(self, fields: list[str] | None = None) -> Iterable[tuple[str, ...]]:
        """Convert rows to columns tuple"""
        for r in self.get_rows():
            for row in r.to_dicts():
                yield tuple(row.get(f, "") for f in fields)

    def add_dataset(self, data: DataSet, name: str | None = None):
        """
        Add dataset
        Attrs:
            data: polars DataFrame
            name: Optional DataSet name, if not set - used band name
        """
        self.datasets[name or self.name] = data

    def set_data(self, data: dict[str, Any]):
        """Set Band Data"""
        self.data.update(data.copy())

    def get_data(self):
        return self.data or {}

    def iter_nested_bands(self) -> Iterable["Band"]:
        """Iterable over nested bands"""
        for b in self.children_bands:
            yield b
            yield from b.iter_nested_bands()

    def get_child_by_name(self, name: str) -> Optional["Band"]:
        """Getting Band by name"""
        for c in self.children_bands:
            if c.name == name:
                return c

    def find_band_recursively(self, name: str) -> Optional["Band"]:
        """Find Band from"""
        if self.name == name:
            return self
        for b in self.iter_nested_bands():
            if b.name == name:
                return b
        return None

    def get_data_band(self) -> "Band":
        """
        Return Leaf Band. First Band without children
        """
        if not self.has_children:
            return self
        for band in self.iter_nested_bands():
            if band.has_rows and not band.has_children:
                return band

    @classmethod
    def from_report(cls, band: ReportBand, params: dict[str, Any] | None = None) -> "Band":
        """Create Band from configuration"""
        return Band(name=band.name, orientation=band.orientation, data=params)

    @classmethod
    def from_band(cls, band: "Band", data: dict[str, Any], parent: Optional["Band"] = None):
        b = Band(
            name=band.name, parent=parent or band.parent, orientation=band.orientation, data=data
        )
        b.datasets = band.datasets
        for c in band.children_bands:
            rb = Band.from_band(c, {}, parent=b.parent)
            rb.datasets = c.datasets
            b.add_child(rb)
        return b

    def iter_report_bands(self, name: str | None = None) -> Iterable["Band"]:
        """
        Iterable bands for report.

        Attrs:
            name: Start band name. if not set - start from root
        1. If root - skip - iterable nested
        2. Return nested
        3. If nested has children - Create Band with row data
        4. If not children - next nest
        """
        if self.is_root and not self.has_children:
            # Nothing reports
            return
        if not self.has_children:
            yield self
            return
        for c in self.children_bands:
            if not c.has_children:
                yield c
                continue
            elif not self.has_rows:
                yield c
                yield from c.iter_report_bands()
            for row in c.iter_rows():
                b = Band.from_band(c, row)
                yield b
                yield from b.iter_report_bands()
