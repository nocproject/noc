# ----------------------------------------------------------------------
# Report Band Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Dict, Any, Iterable, List

# Third-party modules
import polars as pl
from jinja2 import Template as Jinja2Template

# NOC modules
from .types import BandOrientation, ROOT_BAND, ReportBand


@dataclass
class DataSet:
    name: str
    data: pl.DataFrame
    rows: Optional[List[Dict[str, Any]]] = None
    query: Optional[str] = None
    transpose: bool = False


class Band(object):
    """
    Report Data for Band. Contains data, rows and format options
    """

    __slots__ = (
        "name",
        "title_template",
        "parent",
        "orientation",
        "data",
        "children_bands",
        "datasets",
        "format",
        "report_field_format",
    )

    def __init__(
        self,
        name: str,
        parent: Optional["Band"] = None,
        orientation: BandOrientation = BandOrientation.HORIZONTAL,
        data: Dict[str, Any] = None,
    ):
        self.name = name
        self.parent = parent
        self.children_bands: List[Band] = []
        self.orientation = orientation
        self.datasets: Dict[str, DataSet] = {}
        self.data: Dict[str, Any] = data or {}
        # self.rows: Optional[DataFrame] = rows
        # self.format: Optional[BandFormat] = None
        # self.report_field_format: Dict[str, ReportField] = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name} ({self.parent})"

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

    def get_columns(self) -> List[str]:
        r = self.get_rows()
        if not r and not self.data:
            return []
        elif self.data:
            return list(self.data)
        return r[0].columns

    def add_children(self, bands: List["Band"]):
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

    def get_path(self) -> List["Band"]:
        """Getting band path"""
        if self.parent:
            return self.parent.get_path() + [self]
        return [self]

    def get_rows(self) -> List[pl.DataFrame]:
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
            if ds.query and ds.data is None:
                rows = sql.execute(Jinja2Template(ds.query).render(ctx), eager=True)
            elif ds.query and ds.data is not None:
                rows = ds.data.sql(Jinja2Template(ds.query).render(ctx))
            elif not ds.query and ds.data is not None:
                rows = ds.data
            else:
                continue
            if ds.transpose:
                rows = rows.transpose(include_header=True)
            if b.name == self.name:
                r.append(rows)
            else:
                sql.register(b.name, rows.lazy())
        return r

    def iter_rows(self) -> Iterable[Dict[str, Any]]:
        """iterate row dataset"""
        for r in self.get_rows():
            yield from r.to_dicts()

    def add_dataset(self, data: DataSet, name: Optional[str] = None):
        """
        Add dataset
        Attrs:
            data: polars DataFrame
            name: Optional DataSet name, if not set - used band name
        """
        self.datasets[name or self.name] = data

    def set_data(self, data: Dict[str, Any]):
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
    def from_report(cls, band: ReportBand, params: Optional[Dict[str, Any]] = None) -> "Band":
        """Create Band from configuration"""
        return Band(name=band.name, orientation=band.orientation, data=params)

    @classmethod
    def from_band(cls, band: "Band", data: Dict[str, Any], parent: Optional["Band"] = None):
        b = Band(
            name=band.name, parent=parent or band.parent, orientation=band.orientation, data=data
        )
        b.datasets = band.datasets
        for c in band.children_bands:
            rb = Band.from_band(c, {}, parent=b.parent)
            rb.datasets = c.datasets
            b.add_child(rb)
        return b

    def iter_report_bands(self, name: Optional[str] = None) -> Iterable["Band"]:
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
