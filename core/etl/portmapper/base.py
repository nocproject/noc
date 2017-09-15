# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NRI Port mapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


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
    _profile_to_local = {}
    _platform_to_local = {}
    _profile_to_remote = {}
    _platform_to_remote = {}

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
                        if d["local"] and d["profile"]:
                            n._profile_to_local[d["profile"]] = mm
                        elif d["local"] and d["platform"]:
                            n._platform_to_local[d["platform"]] = mm
                        elif not d["local"] and d["profile"]:
                            n._profile_to_remote[d["profile"]] = mm
                        elif not d["local"] and d["platform"]:
                            n._platform_to_remote[d["platform"]] = mm
            return n

    def __init__(self, managed_object):
        self.managed_object = managed_object
        self.profile = self.managed_object.profile.name
        self.platform = self.managed_object.platform

    def to_local(self, name):
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
        else:
            return None

    def to_remote(self, name):
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
        else:
            return None


def to_local(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match += [{"local": True, "profile": profile, "platform": platform}]
        return f

    return wrap


def to_remote(profile=None, platform=None):
    def wrap(f):
        if not hasattr(f, "_match"):
            f._match = []
        f._match += [{"local": False, "profile": profile, "platform": platform}]
        return f

    return wrap
