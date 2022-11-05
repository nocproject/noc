# ----------------------------------------------------------------------
# Qtech.QSW2800.SlotRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib


class EnterpriseRule(OIDRule):
    name = "enterprise"

    def iter_oids(self, script, metric):
        if not script.has_capability("SNMP | OID | EnterpriseID"):
            return
        if len(self.oid) == 2:
            gen = tuple(
                mib[
                    self.expand(
                        o, {"enterprise": script.capabilities["SNMP | OID | EnterpriseID"]}
                    )
                ]
                for o in self.oid
            )
        else:
            gen = mib[
                self.expand(
                    self.oid, {"enterprise": script.capabilities["SNMP | OID | EnterpriseID"]}
                )
            ]
        if gen and "CPU" in metric.metric:
            yield gen, self.type, self.scale, self.units, ("noc::cpu::",)
        elif gen:
            yield gen, self.type, self.scale, self.units, None
