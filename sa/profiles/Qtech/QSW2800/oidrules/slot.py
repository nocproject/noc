# ---------------------------------------------------------------------
# Qtech.QSW2800.SlotRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib


class SlotRule(OIDRule):

    name = "slot"

    def iter_oids(self, script, metric):
        i = 1
        r = {}
        if script.has_capability("Stack | Member Ids"):
            sysSlotIndex = [
                int(index) for index in script.capabilities["Stack | Member Ids"].split(" | ")
            ]
        elif script.has_capability("Stack | Members"):
            sysSlotIndex = list(range(1, script.capabilities["Stack | Members"] + 1))
        else:
            sysSlotIndex = [1]

        for ms in sysSlotIndex:
            r[str(i)] = "%d" % ms
            # r[str(i)] = {"healthModuleSlot": ms}
            i += 1

        for i in r:
            if self.is_complex:
                gen = [mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid]
                labels = (
                    ["noc::chassis::0", "noc::slot::0", f"noc::module::{i}"]
                    if "CPU" in metric.metric
                    else [
                        "noc::chassis::0",
                        f"noc::slot::{i}",
                        "noc::module::0",
                        f"noc::cpu::CPU Slot {i}",
                    ]
                )
                if gen:
                    yield tuple(gen), self.type, self.scale, self.units, labels
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                labels = (
                    ["noc::chassis::0", "noc::slot::0", f"noc::module::{i}"]
                    if "CPU" in metric.metric
                    else [
                        "noc::chassis::0",
                        f"noc::slot::{i}",
                        "noc::module::0",
                        f"noc::cpu::CPU Slot {i}",
                    ]
                )
                if oid:
                    yield oid, self.type, self.scale, self.units, labels
