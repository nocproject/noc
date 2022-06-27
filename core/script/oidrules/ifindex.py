# ----------------------------------------------------------------------
# InterfaceRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class InterfaceRule(OIDRule):
    """
    Expand {{ifIndex}}
    """

    name = "ifindex"

    def iter_oids(self, script, cfg):
        if cfg.ifindex is not None:
            oid = self.expand_oid(ifIndex=cfg.ifindex)
            if oid:
                yield oid, self.type, self.scale, self.units, cfg.labels
