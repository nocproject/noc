# ----------------------------------------------------------------------
# LambdaConstraint class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseConstraint


class LambdaConstraint(BaseConstraint):
    """
    Optical lambda.

    Represented by central frequency and width.

    Args:
        freq: Central frequency in MHz.
        width: Channel width in MHz.
    """

    def __init__(self: "LambdaConstraint", freq: int, width: int) -> None:
        self._freq = freq
        self._width = width

    def __str__(self: "LambdaConstraint") -> str:
        return f"{self._freq}-{self._width}"

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, LambdaConstraint)
            and self._freq == value._freq
            and self._width == value._width
        )

    @property
    def min_freq(self: "LambdaConstraint") -> int:
        """Minimal frequency in GHz."""
        return self._freq - self._width // 2

    @property
    def max_freq(self: "LambdaConstraint") -> int:
        """Maximal frequency in GHz."""
        return self._freq + self._width // 2

    @classmethod
    def from_discriminator(cls: "type[LambdaConstraint]", v: str) -> "LambdaConstraint":
        """Create constraint from lambda discriminator."""
        freq, width = v[8:].split("-")
        return LambdaConstraint(int(freq) * 1_000, int(width) * 1_000)

    @property
    def discriminator(self: "LambdaConstraint") -> str:
        """Convert to discriminator."""
        return f"lambda::{self._freq // 1_000}-{self._width // 1_000}"

    @property
    def humanized(self: "LambdaConstraint") -> str:
        """
        Convert to human-readable string.
        """
        if self._width % 1_000 == 0:
            w = f"{self._width // 1_000} GHz"
        else:
            w = f"{float(self._width) / 1_000.0} GHz"
        # C-band?
        offset = self._freq - C1
        if offset % G100 == 0:
            n = (offset // G100) + 1
            return f"C{n} ({w})"
        return f"{self._freq / 1_000} GHz ({w})"

    @property
    def frequency(self) -> int:
        """Frequency (MHz)"""
        return self._freq

    @property
    def width(self) -> int:
        """Channel width (MHz)"""
        return self._width


C1 = 190_100_000
G100 = 100_000
