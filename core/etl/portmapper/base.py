# ----------------------------------------------------------------------
# NRI Port mapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# Python modules
from typing import Any, cast

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


class PortMapperBase(type):
    """
    Process @match decorators
    """

    def __new__(
        mcs: "type[PortMapperBase]",
        name: str,
        bases: tuple[type[Any], ...],
        attrs: dict[str, Any],
    ) -> type["BasePortMapper"]:
        n = cast(type["BasePortMapper"], type.__new__(mcs, name, bases, attrs))
        for m in dir(n):
            mm = getattr(n, m)
            if hasattr(mm, "_match"):
                for d in mm._match:
                    if d["local"] and d["profile"]:
                        n._profile_to_local[d["profile"]] = mm
                    elif d["local"] and d["platform"]:
                        n._platform_to_local[d["platform"]] = mm
                    elif not d["local"] and d["profile"]:
                        n._profile_to_remote[d["profile"]] = mm
                    elif not d["local"] and d["platform"]:
                        n._platform_to_remote[d["platform"]] = mm
        return n


class BasePortMapper(metaclass=PortMapperBase):
    """
    Basic class to convert port notation from external NRI and back.
    External NRI system is defined in managed object's
    src:<SYSTEM> tag.

    NRI format converted to NOC's one via methods decorated with
    @from_mapping()

    NOC's format converted to NRI's one via methods decorated with
    @to_mappings()
    """

    _profile_to_local = {}
    _platform_to_local = {}
    _profile_to_remote = {}
    _platform_to_remote = {}

    def __init__(self, managed_object) -> None:
        self.managed_object = managed_object
        self.profile = self.managed_object.profile.name
        self.platform = self.managed_object.platform.name if self.managed_object.platform else None

    def to_local(self, name, iface_hints=None):
        """
        Convert interface name from NRI to NOC's conventions
        """
        if self.platform:
            mm = self._platform_to_local.get(self.platform)
            if mm:
                return mm(self, name)
        mm = self._profile_to_local.get(self.profile)
        if mm:
            return mm(self, name)
        return None

    def to_remote(self, name, iface_hints=None):
        """
        Convert interface name
        """
        if self.platform:
            mm = self._platform_to_remote.get(self.platform)
            if mm:
                return mm(self, name)
        mm = self._profile_to_remote.get(self.profile)
        if mm:
            return mm(self, name)
        return None


def to_local(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match.append({"local": True, "profile": profile, "platform": platform})
        return f

    return wrap


def to_remote(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match.append({"local": False, "profile": profile, "platform": platform})
        return f

    return wrap


portmapper_loader = Loader[type[BasePortMapper]](
    bases=config.iter_customized_bases("noc.core.etl.portmapper"),
    exclude=("base",),
)
