# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HiresRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .loader import load_rule


class HiresRule(object):
    """
    Select *hires* chain if SNMP | IF-MIB HC capability set,
    Select *normal* capability otherwise
    """
    name = "hires"

    def __init__(self, hires, normal):
        self.hires = hires
        self.normal = normal

    def iter_oids(self, script, metric):
        if script.has_capability("SNMP | IF-MIB | HC"):
            g = self.hires.iter_oids
        else:
            g = self.normal.iter_oids
        for r in g(script, metric):
            yield r

    @classmethod
    def from_json(cls, data):
        for v in ("hires", "normal"):
            if v not in data:
                raise ValueError("%s is required" % v)
        return HiresRule(
            hires=load_rule(data["hires"]),
            normal=load_rule(data["normal"])
        )
