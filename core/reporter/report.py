# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, Iterable, List
from collections import defaultdict

# Third-party modules
from polars import DataFrame

# NOC modules
from .types import BandOrientation, ReportField, BandFormat


class BandData(object):
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
        "rows",
        "format",
        "report_field_format",
    )

    ROOT_BAND_NAME = "Root"

    def __init__(
        self,
        name: str,
        parent_band: Optional["BandData"] = None,
        orientation: BandOrientation = BandOrientation.HORIZONTAL,
        rows=None,
    ):
        self.name = name
        self.parent = parent_band
        self.orientation = orientation
        self.data: Dict[str, Any] = {}
        self.children_bands: Dict[str, List["BandData"]] = defaultdict(list)
        self.rows: Optional[DataFrame] = rows
        self.format: Optional[BandFormat] = None
        self.report_field_format: Dict[str, ReportField] = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name} ({self.parent})"

    @property
    def is_root(self) -> bool:
        """
        Return True if Root Band
        :return:
        """
        return self.name == self.ROOT_BAND_NAME

    @property
    def has_children(self) -> bool:
        return bool(self.children_bands)

    @property
    def has_rows(self) -> bool:
        return self.rows is not None and not self.rows.is_empty()

    def iter_children_bands(self) -> Iterable["BandData"]:
        """
        Iterate over children bands
        :return:
        """
        for b in self.children_bands.values():
            yield from b

    @property
    def full_name(self):
        """
        Calculate full BandName - <rb>.<b1>.<b2>
        :return:
        """
        if not self.parent or self.is_root:
            return self.name
        path = [self.name]
        parent = self.parent
        while parent and not parent.is_root:
            path.append(parent.name)
            parent = parent.parent
        return ".".join(reversed(path))

    def add_children(self, bands: List["BandData"]):
        """
        Add children Band
        :param bands:
        :return:
        """
        for b in bands:
            self.add_child(b)

    def add_child(self, band: "BandData"):
        band.parent = self
        self.children_bands[band.name].append(band)

    def set_data(self, data: Dict[str, Any]):
        """
        Set Band Data
        :param data:
        :return:
        """
        self.data.update(data.copy())

    def get_data(self):
        return self.data or {}

    def get_children_by_name(self, name: str) -> List["BandData"]:
        """
        Return Children Bands by name
        :param name:
        :return:
        """
        return self.children_bands.get(name, [])

    def get_child_by_name(self, name: str) -> Optional["BandData"]:
        """

        :param name:
        :return:
        """
        if name not in self.children_bands:
            return None
        return self.children_bands[name][0]

    def iter_all_bands(self) -> Iterable["BandData"]:
        """
        Iterate over nested bands from current
        :return:
        """
        for c_bands in self.children_bands.values():
            for band in c_bands:
                yield band
                yield from band.iter_all_bands()

    def find_band_recursively(self, name: str) -> Optional["BandData"]:
        """

        :param name:
        :return:
        """
        if self.name == name:
            return self
        for b in self.iter_all_bands():
            if b.name == name:
                return b
        return None

    def get_data_band(self) -> "BandData":
        """
        Return Leaf Band. First Band without children
        """
        if not self.has_children:
            return self
        for band in self.iter_all_bands():
            if band.rows is not None and not band.has_children:
                return band
