# ----------------------------------------------------------------------
# Huawei.VRP.SlotRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.oidrules.oid import OIDRule
from noc.core.mib import mib


class SlotRule(OIDRule):
    name = "slot"

    def iter_oids(self, script, metric):
        hwFrameIndex = [0]
        hwSlotIndex = [0]
        hwCpuDevIndex = [0]

        if script.has_capability("Stack | Members"):
            hwSlotIndex = list(range(script.capabilities["Stack | Members"]))
        i = 0
        r = {}

        for fi in hwFrameIndex:
            for si in hwSlotIndex:
                for cp in hwCpuDevIndex:
                    r[str(i)] = "%d.%d.%d" % (fi, si, cp)
                    # r[str(i)] = {"hwFrameIndex": fi, "hwSlotIndex": si, "hwCpuDevIndex": cp}
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
