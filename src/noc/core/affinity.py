# ----------------------------------------------------------------------
# CPU Affinity utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from typing import Final, ClassVar
import random


class _Auto:
    """Automatic CPU affinity detection sentinel."""


class _None:
    """CPU affinity unavailable sentinel."""


AFF_AUTO: Final = _Auto()
AFF_NONE: Final = _None()


class BaseController:
    supports_set: ClassVar[bool] = False

    @classmethod
    def get_affinity(cls) -> set[int] | _None:
        """Get the CPU affinity of the current process.

        Returns:
            set[int]: Set of CPU numbers the process is allowed to run on.
            _None: CPU affinity is not supported by the operating system.
        """
        return AFF_NONE

    @classmethod
    def set_affinity(cls, mask: set[int]) -> None:
        """Set the CPU affinity of the current process.

        Args:
            mask (set[int]): Set of CPU numbers the process should be allowed to
                run on.
        """

    @classmethod
    def parse_affinity(cls, aff: str) -> set[int] | _Auto | _None:
        """Parse a CPU affinity specification.

        Args:
            aff (str): CPU affinity specification. ``auto`` enables automatic
                detection, ``none`` disables CPU affinity, and a
                comma-separated list specifies CPU numbers explicitly.

        Returns:
            set[int]: Explicitly specified CPU numbers.
            _Auto: Automatic CPU affinity detection requested.
            _None: CPU affinity disabled.
        """
        aff = aff.strip()
        if not aff or aff == "none":
            return AFF_NONE
        if aff == "auto":
            return AFF_AUTO
        return {int(item.strip()) for item in aff.split(",")}

    @classmethod
    def effective_affinity(cls, aff: str) -> set[int] | _None:
        """Calculate the effective CPU affinity.

        The effective affinity is calculated as the intersection of the
        requested affinity and the process affinity. For ``auto``, one CPU
        is selected randomly from the process affinity.

        Args:
            aff (str): CPU affinity specification.

        Returns:
            set[int]: Effective CPU affinity.
            _None: CPU affinity cannot be determined or no requested CPUs are
                available.
        """
        expected = cls.parse_affinity(aff)
        if isinstance(expected, _None):
            return AFF_NONE
        mask = cls.get_affinity()
        if isinstance(mask, _None) or not mask:
            return AFF_NONE
        if isinstance(expected, _Auto):
            return {random.choice(list(mask))}
        r = mask.intersection(expected)
        if r:
            return r
        return AFF_NONE


class LinuxAffinityController(BaseController):
    supports_set: ClassVar[bool] = True

    @classmethod
    def get_affinity(cls) -> set[int] | _None:
        """Get the CPU affinity of the current process.

        Returns:
            set[int]: Set of CPU numbers the process is allowed to run on.
            _None: CPU affinity is not supported by the operating system.
        """
        return os.sched_getaffinity(0)

    @classmethod
    def set_affinity(cls, mask: set[int]) -> None:
        """Set the CPU affinity of the current process.

        Args:
            mask (set[int]): Set of CPU numbers the process should be allowed to
                run on.
        """
        return os.sched_setaffinity(0, mask)


AffinityController = BaseController
if hasattr(os, "sched_getaffinity"):
    AffinityController = LinuxAffinityController
