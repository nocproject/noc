# ----------------------------------------------------------------------
# Huawei.MA5600T
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.oidrules.oid import OIDRule
from noc.core.mib import mib


class HWSlots(OIDRule):
    name = "hwslots"

    def iter_oids(self, script, metric, **kwargs):
        if metric.metric == "Environment | Temperature":
            slots = script.capabilities["Slot | Member Ids | Temperature"].split(" | ")
        else:
            return

        r = script.snmp.get_chunked([f"1.3.6.1.4.1.2011.6.3.3.2.1.21.0.{s}" for s in slots])
        slot_names = {k.split(".")[-1]: r[k] for k in r}
        if not slot_names:
            # Sometimes slot names is empty
            return
        for slot in slots:
            if self.is_complex:
                gen = [mib[self.expand(o, {"item": slot})] for o in self.oid]
                labels = [
                    "noc::chassis::0",
                    f"noc::slot::{slot}",
                    f"noc::sensor::Temperature Sensor ({slot_names[slot]})",
                ]
                if gen:
                    yield tuple(gen), self.type, self.scale, "C", labels
            else:
                oid = mib[self.expand(self.oid, {"item": slot})]
                labels = [
                    "noc::chassis::0",
                    f"noc::slot::{slot}",
                    "noc::sensor::Temperature Sensor (%s)" % slot_names[slot],
                ]
                if oid:
                    yield oid, self.type, self.scale, "C", labels
