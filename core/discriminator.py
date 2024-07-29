# ----------------------------------------------------------------------
# Lambda discriminator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Union, Set, List, Tuple, Iterable

# NOC modules
from noc.core.text import ranges_to_list


SCOPE_SEPARATOR = "::"


class LambdaDiscriminator(object):
    """
    Optical wavelength.

    Possible formats:
        * `<freq>` - central frequency in GHz
        * `<freq>-<width>` - central frequency and channel width in GHz.
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
        if not isinstance(other, VlanDiscriminator):
            return False
        return self.vlan == other.vlan or other.vlan.issubset(self.vlan)


# ODU -> Nested ODU -> limit
ODU_LIMITS = {
    "ODU0": {},
    "ODU1": {"ODU0": 2},
    "ODU2": {"ODU0": 8, "ODU1": 4},
    "ODU2e": {},
    "ODU3": {"ODU0": 32, "ODU1": 16, "ODU2e": 1},
    "ODU3e2": {"ODU2e": 4},
    "ODU4": {"ODU0": 80, "ODU1": 40, "ODU2": 10, "ODU2e": 10, "ODU3": 2},
    "ODUC1": {"ODU4": 1},
    "ODUC2": {"ODU4": 2, "ODU2": 20},
    "ODUC3": {"ODU4": 3},
    "ODUC4": {"ODU4": 4},
    "ODUC5": {"ODU4": 5},
    "ODUC6": {"ODU4": 6},
}


class OduDiscriminator(object):
    scope: str = "odu"

    def __init__(self, value: str):
        self.odu: List[Tuple[str, int]] = list(self._iter_parse(value))
        # Check odu
        prev_odu = None
        for n, idx in self.odu:
            if n not in ODU_LIMITS:
                msg = f"Invalid ODU type: {n}"
                raise ValueError(msg)
            if prev_odu:
                if n not in ODU_LIMITS[prev_odu]:
                    msg = f"{n} cannot be nested in {prev_odu}"
                    raise ValueError(msg)
                max_idx = ODU_LIMITS[prev_odu][n]
                if idx > max_idx:
                    msg = f"ODU index overflow: {idx} >= {max_idx}"
                    raise ValueError(msg)
            elif idx:
                msg = "Top-level ODU must have index 0"
                raise ValueError(msg)
            prev_odu = n

    @staticmethod
    def _iter_parse(value: str) -> Iterable[Tuple[str, int]]:
        def q(x: str) -> Tuple[str, int]:
            if "-" in x:
                n, y = x.split("-", 1)
                return n, int(y)
            return x, 0

        for x in value.split("::"):
            yield q(x)

    def __str__(self) -> str:
        r = [self.odu[0][0]]
        for n, idx in self.odu[1:]:
            r.append(f"{n}-{idx}")
        return f"{self.scope}::{'::'.join(r)}"

    def __contains__(self, other: "OduDiscriminator") -> bool:
        if not isinstance(other, OduDiscriminator):
            return False
        if self.odu == other.odu:
            return True
        if len(self.odu) > len(other.odu):
            return False
        return self.odu == other.odu[: len(self.odu)]

    def get_limit(self, d: "OduDiscriminator") -> int:
        """
        Return Multiplex Limit
        :param d: Payload
        # :param d2: Container
        :return:
        """
        if self.odu == d.odu:
            return 1
        if d not in self:
            return 0
        # Container
        c, cn = self.odu[0]
        # Payload
        p, pn = d.odu[0]
        if p not in ODU_LIMITS[c]:
            return 0
        return ODU_LIMITS[c][p]

    def get_crossing_proposals(self, d: Union[str, "OduDiscriminator"]) -> List[str]:
        """
        Same discriminator - container
        :param d: Payload
        :return:
        """
        if isinstance(d, str):
            d = discriminator(d)
        limit = self.get_limit(d)
        if not limit:
            return []
        elif limit == 1:
            return [f"{self.scope}::{self.odu[0][0]}"]
        r = []
        for n in range(1, limit + 1):
            r.append(f"{self.scope}::{self.odu[0][0]}::{d.odu[0][0]}-{n}")
        return r


scopes = {x.scope: x for x in (LambdaDiscriminator, VlanDiscriminator, OduDiscriminator)}


def discriminator(v: str) -> Union[LambdaDiscriminator, VlanDiscriminator, OduDiscriminator]:
    if SCOPE_SEPARATOR not in v:
        msg = "Invalid Format"
        raise ValueError(msg)
    scope, value = v.split(SCOPE_SEPARATOR, 1)
    kls = scopes.get(scope)
    if kls:
        return kls(value)
    msg = f"Unknown discriminator: {scope}"
    raise ValueError(msg)
