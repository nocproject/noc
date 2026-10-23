# ----------------------------------------------------------------------
# Rotek.RTBSv1.oidrules.platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.oidrules.oid import OIDRule
from noc.core.mib import mib


class PlatformRule(OIDRule):
    name = "platform"

    def iter_oids(self, script, cfg):
        ent_id = script.profile.get_ent_id(script)
        oid = mib[self.expand(self.oid, {"platform": ent_id, "ifIndex": cfg.ifindex})]
        if oid:
            yield oid, self.type, self.scale, self.units, cfg.labels
