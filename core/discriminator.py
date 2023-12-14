# ----------------------------------------------------------------------
# Lambda discriminator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Union, Set

# NOC modules
from noc.core.text import ranges_to_list


SCOPE_SEPARATOR = "::"


class LambdaDiscriminator(object):
    """
    Optical wavelength.

    Possible formats:
        * `<freq>` - central frequence in GHz
        * `<freq>-<width>` - central frequence and channel width in GHz.
    """

    scope: str = "lambda"

    def __init__(self, value: str) -> None:
        if "-" in value:
            f, w = value.split("-")
        else:
            f, w = value, "0"
        self.freq = int(f)
        self.width = int(w)

    def __str__(self) -> str:
        if self.width:
            return f"{self.scope}{SCOPE_SEPARATOR}{self.freq}-{self.width}"
        return f"{self.scope}{SCOPE_SEPARATOR}{self.freq}-{self.width}"

    def __contains__(self, other: Any) -> bool:
        if not isinstance(other, LambdaDiscriminator):
            return False
        if not self.width:
            return True
        if not other.width:
            return False
        return ((self.freq - self.width) <= (other.freq - other.width)) and (
            (self.freq + self.width) >= (other.freq + other.width)
        )


class VlanDiscriminator(object):
    scope: str = "vlan"

    def __init__(self, value: str):
        try:
            self.vlan: Set[int] = set(ranges_to_list(value))
        except SyntaxError as e:
            msg = f"Invalid VLAN: {value}"
            raise ValueError(msg) from e
        if any(v < 1 or v > 4095 for v in self.vlan):
            msg = f"Invalid VLAN: {value}"
            raise ValueError(msg)

    def __str__(self) -> str:
        return f"{self.scope}{SCOPE_SEPARATOR}{self.vlan}"

    def __contains__(self, other: Any) -> bool:
        # @todo: VLAN Filter support
        if not isinstance(other, VlanDiscriminator):
            return False
        print(self.vlan)
        print(other.vlan)
        return self.vlan == other.vlan or other.vlan.issubset(self.vlan)


scopes = {x.scope: x for x in (LambdaDiscriminator, VlanDiscriminator)}


def discriminator(v: str) -> Union[LambdaDiscriminator, VlanDiscriminator]:
    if SCOPE_SEPARATOR not in v:
        msg = "Invalid Format"
        raise ValueError(msg)
    scope, value = v.split(SCOPE_SEPARATOR, 1)
    kls = scopes.get(scope)
    if kls:
        return kls(value)
    msg = f"Unknown discriminator: {scope}"
    raise ValueError(msg)
