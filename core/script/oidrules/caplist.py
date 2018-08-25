# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CapabilityListRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .oid import OIDRule


class CapabilityListRule(OIDRule):
    """
    Expand {{item}} from capability
    capability: String capability, separated by *separator*
    separator: String separator, comma by default
    strip: Strip resulting item, remove spaces from both sides
    """
    name = "caplist"

    def __init__(self, oid, type=None, scale=1, capability=None,
                 separator=",", strip=True, default=None, path=None):
        super(CapabilityListRule, self).__init__(oid, type=type, scale=scale)
        self.capability = capability
        self.separator = separator
        self.strip = strip
        self.default = default
        self.path = path

    def iter_oids(self, script, cfg):
        if self.capability and script.has_capability(self.capability):
            for i in script.capabilities[self.capability].split(self.separator):
                if self.strip:
                    i = i.strip()
                if not i:
                    continue
                oid = self.expand_oid(item=i)
                path = cfg.path
                if self.path is not None and "item" in self.path:
                    path = self.path[:]
                    path[self.path.index("item")] = i
                if oid:
                    yield oid, self.type, self.scale, path
        else:
            if self.default is not None:
                oid = self.expand_oid(item=self.default)
                if oid:
                    yield oid, self.type, self.scale, cfg.path
