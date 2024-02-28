# ----------------------------------------------------------------------
# Protocol Discriminator Source loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
from typing import List, Iterable

# NOC modules
from .base import BaseDiscriminatorSource, DiscriminatorDataItem
from noc.core.discriminator import LambdaDiscriminator

GRID_BASE = 192.1 * 1_000
GRID_STEP = 0.05 * 1_000


class OpticalDWDMDiscriminatorSource(BaseDiscriminatorSource):
    """
    Check ManagedObject profile by rules
    """

    name = "optical_dwdm"

    frequency_wl_map = {
        192.1: 1560.61,
        192.15: 1560.20,
        192.2: 1559.79,
        192.25: 1559.39,
        194.75: 1539.37,
    }

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """
        for num, lit in itertools.product(range(21, 61), "CH"):
            yield f"{lit}{num}"

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """
        lit, num = item[0], item[1:]
        if lit not in {"C", "H"} or int(num) < 21 or int(num) > 60:
            return False
        return True

    def get_data(self, code: str) -> List[DiscriminatorDataItem]:
        """
        Get Discriminator Data by code
        C21 - > 1560,61
        """
        lit, num = code[0], code[1:]
        tx = 192.1 + (int(num) - 21) * 0.1
        if lit == "H":
            tx += 0.05
            # tx_frequency
        return [
            DiscriminatorDataItem("dwdm", "tx_frequency", tx),
            DiscriminatorDataItem(
                "optical", "tx_wavelength", self.frequency_wl_map.get(tx, 1560.61)
            ),
        ]

    def get_code(self, data: List[DiscriminatorDataItem]) -> str:
        """
        Get Discriminator Code by data
        """
        for d in data:
            if d.interface == "dwdm" and d.attr == "tx_frequency":
                r = list(self)
                num = int((d.value * 1_000 - GRID_BASE) / GRID_STEP)
                return r[num]
        raise ValueError("Not found code for data")

    def get_discriminator_instance(self, code):
        freq, wl = self.get_data(code)
        return LambdaDiscriminator(f"{freq.value * 1000}-50")
