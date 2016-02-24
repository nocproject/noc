# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NRI Port mapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class BasePortMapper(object):
    """
    Basic class to convert port notation from external NRI and back.
    External NRI system is defined in managed object's
    src:<SYSTEM> tag.

    NRI format converted to NOC's one via methods decorated with
    @from_mapping()

    NOC's format converted to NRI's one via methods decorated with
    @to_mappings()
    """
    _from_profile_mappings = {}
    _from_platform_mappings = {}
    _to_profile_mappings = {}
    _to_platform_mappings = {}

    class __metaclass__(type):
        """
        Process @match decorators
        """
        def __new__(mcs, name, bases, attrs):
            n = type.__new__(mcs, name, bases, attrs)
            for m in dir(n):
                mm = getattr(n, m)
                if hasattr(mm, "_match"):
                    for d in mm._match:
                        if d["from"] and d["profile"]:
                            m._from_profile_mappings[d["profile"]] = mm
                        elif d["from"] and d["platform"]:
                            m._from_platform_mappings[d["platform"]] = mm
                        elif not d["from"] and d["profile"]:
                            m._to_profile_mappings[d["profile"]] = mm
                        elif not d["from"] and d["plaform"]:
                            m._to_platform_mappings[d["platform"]] = mm
            return n

    def __init__(self, managed_object):
        self.managed_object = managed_object
        self.profile = self.managed_object.profile_name
        self.platform = self.managed_object.platform

    def to_local(self, name):
        """
        Convert interface name from NRI to NOC's conventions
        """
        if self.platform:
            mm = self._to_platform_mappings.get(self.platform)
            if mm:
                return mm(name)
        mm = self._to_profile_mappings.get(self.profile)
        if mm:
            return mm(name)
        else:
            return None

    def to_remote(self, name):
        """
        Convert interface name
        """
        if self.platform:
            mm = self._from_platform_mappings.get(self.platform)
            if mm:
                return mm(name)
        mm = self._from_profile_mappings.get(self.profile)
        if mm:
            return mm(name)
        else:
            return None


def from_mapping(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match += [{"from": True, "profile": profile, "platform": platform}]
        return f

    return wrap


def to_mapping(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match += [{"from": False, "profile": profile, "platform": platform}]
        return f

    return wrap
