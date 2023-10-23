# ----------------------------------------------------------------------
# Protocol Discriminator Source loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

# NOC modules
from .base import BaseDiscriminatorSource, DiscriminatorDataItem


class ProtocolDiscriminatorSource(BaseDiscriminatorSource):
    """
    Check ManagedObject profile by rules
    """

    name = "protocol"

    codes = {}

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """
        for d in self.protocol.discriminators:
            yield d.code

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """
        self.load_data()
        return item in self.codes

    def get_data(self, code: str) -> List[DiscriminatorDataItem]:
        """
        Get Discriminator Data by code
        """
        self.load_data()
        return self.codes.get(code) or []

    def get_code(self, data: List[DiscriminatorDataItem]) -> str:
        """
        Get Discriminator Code by data
        """
        for d in self.protocol.discriminators:
            if d.data == data[0]:
                return d.code

    def load_data(self):
        if self.codes:
            return
        for d in self.protocol.discriminators:
            self.codes[d.code] = d.data
