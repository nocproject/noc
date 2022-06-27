# ----------------------------------------------------------------------
# Huawei.VRP.SSlotRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.oidrules.oid import OIDRule
from noc.core.mib import mib


class SSlotRule(OIDRule):
    name = "sslot"

    def iter_oids(self, script, metric):
        hwSlotIndex = [0]
        hwModIndex = [0, 1]

        if script.has_capability("Slot | Member Ids"):
            hwSlotIndex = script.capabilities["Slot | Member Ids"].split(" | ")
        r = {}

        for si in hwSlotIndex:
            for cp in hwModIndex:
                r[(int(si), cp)] = "%d.%d" % (int(si), cp)

        for si, cp in r:
            if self.is_complex:
                gen = [mib[self.expand(o, {"hwSlotIndex": r[(si, cp)]})] for o in self.oid]
                labels = [
                    "noc::chassis::0",
                    f"noc::slot::{si}",
                    f"noc::module::{cp}",
                    f"noc::cpu::CPU Slot {si}/{cp}",
                ]
                if gen:
                    yield tuple(gen), self.type, self.scale, self.units, labels
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[(si, cp)]})]
                labels = [
                    "noc::chassis::0",
                    f"noc::slot::{si}",
                    f"noc::module::{cp}",
                    f"noc::cpu::CPU Slot {si}/{cp}",
                ]
                if oid:
                    yield oid, self.type, self.scale, self.units, labels
