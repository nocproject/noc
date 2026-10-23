# ----------------------------------------------------------------------
# OIDsRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class OIDsRule:
    """Multiple items for single metric"""

    name = "oids"

    def __init__(self, oids) -> None:
        self.oids = oids

    def iter_oids(self, script, metric):
        for rule in self.oids:
            yield from rule.iter_oids(script, metric)

    @classmethod
    def from_json(cls, data):
        if "oids" not in data:
            raise ValueError("oids is required")
        if not isinstance(data["oids"], list):
            raise ValueError("oids must be list")
        return OIDsRule(oids=[OIDRule.from_json(d) for d in data["oids"]])
