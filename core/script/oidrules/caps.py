# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CapabilityRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .loader import load_rule


class CapabilityRule(object):
    """
    Capability-based selection

    oids is the list of (Capability, OIDRule)
    """
    name = "caps"

    def __init__(self, oids):
        self.oids = oids

    def iter_oids(self, script, metric):
        for cap, oid in self.oids:
            if script.has_capability(cap):
                for r in oid.iter_oids(script, metric):
                    yield r
                break

    @classmethod
    def from_json(cls, data):
        if "oids" not in data:
            raise ValueError("oids is required")
        if type(data["oids"]) != list:
            raise ValueError("oids must be list")
        return CapabilityRule(
            oids=[load_rule(d) for d in data["oids"]]
        )
