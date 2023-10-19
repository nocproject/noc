# ----------------------------------------------------------------------
# DiscriminatorSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Iterable
from noc.inv.models.protocol import Protocol, ProtocolAttr


@dataclass(frozen=True)
class ProtocolDataItem(object):
    interface: str
    attr: str
    value: str


class BaseDiscriminatorSource(object):
    """DataSource and fields description"""

    name: str

    def __init__(self, protocol: "Protocol", data: List[ProtocolAttr] = None):
        self.protocol = protocol
        self.data = data

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """
        ...

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """
        ...

    def get_data(self, code: str) -> List[ProtocolAttr]:
        """
        Get Discriminator Data by code
        """
        ...

    def get_code(self, data: List[ProtocolAttr]) -> str:
        """
        Get Discriminator Code by data
        """
        ...
