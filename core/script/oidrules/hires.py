# ----------------------------------------------------------------------
# HiresRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

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
        flag = False
        if script.has_capability("SNMP | IF-MIB | HC"):
            g = self.hires.iter_oids
        else:
            g = self.normal.iter_oids
            flag = True
        for oid, type, scale, units, labels in g(script, metric):
            yield oid, type, scale, f"{units}|1" if flag else units, labels

    @classmethod
    def from_json(cls, data):
        for v in ("hires", "normal"):
            if v not in data:
                raise ValueError(f"{v} is required")
        return HiresRule(hires=load_rule(data["hires"]), normal=load_rule(data["normal"]))
