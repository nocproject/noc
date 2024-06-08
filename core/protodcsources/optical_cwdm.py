# ----------------------------------------------------------------------
# Protocol Discriminator Source loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import List, Iterable

# NOC modules
from .base import BaseDiscriminatorSource, DiscriminatorDataItem


class CWDMChannel(enum.Enum):
    C27 = 1270  # Grey, 235.87
    C29 = 1290  # Grey, 232.22
    C31 = 1310  # Grey, 228.67
    C33 = 1330  # Violet
    C35 = 1350  # Blue
    C37 = 1370  # Green
    C39 = 1390  # Yellow
    C41 = 1410  # Orange
    C43 = 1430  # Red
    C45 = 1450  # Brown
    C47 = 1470  # Grey
    C49 = 1490  # Violet
    C51 = 1510  # Blue
    C53 = 1530  # Green
    C55 = 1550  # Yellow
    C57 = 1570  # Orange
    C59 = 1590  # Red
    C61 = 1610  # Brown


class ProtocolDiscriminatorSource(BaseDiscriminatorSource):
    """
    Check ManagedObject profile by rules
    """

    name = "optical_cwdm"

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """
        for c in CWDMChannel:
            yield str(c.value)

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """
        try:
            CWDMChannel(item)
        except ValueError:
            return False
        return True

    def get_data(self, code: str) -> List[DiscriminatorDataItem]:
        """
        Get Discriminator Data by code
        """
        return [DiscriminatorDataItem("optical", "tx_wavelength", int(code) + 1)]

    def get_code(self, data: List[DiscriminatorDataItem]) -> str:
        """
        Get Discriminator Code by data
        """
        for d in data:
            if d.interface == "optical" and d.attr == "tx_wavelength":
                c = CWDMChannel(d.value)
                return str(c.value)
        raise ValueError("Not found code for data")
