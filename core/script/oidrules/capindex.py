# ----------------------------------------------------------------------
# CapabilityIndexRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class CapabilityIndexRule(OIDRule):
    """
    Expand {{index}} to range given in capability
    capability: Integer capability containing number of iterations
    start: starting index
    """

    name = "capindex"

    def __init__(self, oid, type=None, scale=1, start=0, capability=None):
        super().__init__(oid, type=type, scale=scale)
        self.start = start
        self.capability = capability

    def iter_oids(self, script, cfg):
        if self.capability and script.has_capability(self.capability):
            for i in range(self.start, script.capabilities[self.capability] + self.start):
                oid = self.expand_oid(index=i)
                if oid:
                    yield oid, self.type, self.scale, self.units, cfg.labels
