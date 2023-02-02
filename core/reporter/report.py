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
from .types import BandOrientation, ReportField


class BandData(object):
    """
    Report Data for Band
    """

    __slots__ = (
        "name",
        "parent",
        "orientation",
        "data",
        "children_bands",
        "rows",
        "report_field_format",
    )

    ROOT_BAND_NAME = "Root"

    def __init__(
        self,
        name: str,
        parent_band: Optional["BandData"] = None,
        orientation: BandOrientation = BandOrientation.HORIZONTAL,
    ):
        self.name = name
        self.parent = parent_band
        self.orientation = orientation
        self.data: Dict[str, Any] = {}
        self.children_bands: Dict[str, List["BandData"]] = defaultdict(list)
        self.rows: Optional[DataFrame] = None
        self.report_field_format: Dict[str, ReportField] = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name} ({self.parent})"

    @property
    def is_root(self) -> bool:
        return self.name == self.ROOT_BAND_NAME

    def iter_children_bands(self) -> Iterable["BandData"]:
        """
        Itarate over children bands
        :return:
        """
        for b in self.children_bands.values():
            yield from b

    @property
    def full_name(self):
        if not self.parent or self.is_root:
            return self.name
        path = [self.name]
        parent = self.parent
        while parent and not parent.is_root:
            path.append(parent.name)
            parent = parent.parent
        return ".".join(reversed(path))

    def add_children(self, bands: List["BandData"]):
        for b in bands:
            self.add_child(b)

    def add_child(self, band: "BandData"):
        # if band.name not in self.children_bands:
        self.children_bands[band.name].append(band)

    def set_data(self, data: Dict[str, Any]):
        self.data.update(data.copy())

    def get_data(self):
        return self.data or {}

    def get_children_by_name(self, name: str) -> List["BandData"]:
        """

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
