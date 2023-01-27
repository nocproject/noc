# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, Iterable, List

# Third-party modules
from polars import DataFrame

# NOC modules
from .types import BandOrientation, ReportField


class BandData(object):
    """
    Report Data for Band
    """

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
        self.children_bands: Dict[str, "BandData"] = {}
        self.rows: Optional[DataFrame] = None
        self.report_field_format: Dict[str, ReportField] = {}

    def iter_children_bands(self) -> Iterable["BandData"]:
        """
        Itarate over children bands
        :return:
        """
        for b in self.children_bands:
            yield b

    @property
    def full_name(self):
        if not self.parent:
            return self.name
        return f"{self.parent.name}.{self.name}"

    def add_children(self, bands: List["BandData"]):
        for b in bands:
            self.add_child(b)

    def add_child(self, band: "BandData"):
        if band.name not in self.children_bands:
            self.children_bands[band.name] = band

    def set_data(self, data: Dict[str, Any]):
        self.data.update(data.copy())
