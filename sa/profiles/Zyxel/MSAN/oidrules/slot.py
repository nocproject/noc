# ---------------------------------------------------------------------
# Zyxel.MSAN.SlotRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib


class SlotRule(OIDRule):
    name = "slot"

    def get_label(self, metric, slot, board_name):
        if "cpu" in metric.lower():
            metric_label = "cpu"
            unit = "%"

        return [
            unit,
            [
                f"noc::slot::{slot}",
                f"noc::{metric_label}::{board_name}",
            ],
        ]

    def iter_oids(self, script, metric):
        i = 1
        r = {}
        if script.has_capability("Stack | Member Ids"):
            ssi = [int(index) for index in script.capabilities["Stack | Member Ids"].split(" | ")]
        elif script.has_capability("Stack | Members"):
            ssi = list(range(1, script.capabilities["Stack | Members"] + 1))
        else:
            ssi = [1]
        for ms in ssi:
            r[str(i)] = int(ms)
            i += 1
        for i in r:
            if self.is_complex:
                gen = tuple(mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid)
            else:
                gen = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
            if not gen:
                continue
            slot_desc_oid = f"1.3.6.1.4.1.890.1.5.13.1.1.3.1.3.0.{r[i]}"
            slot_descr = script.snmp.get(slot_desc_oid)
            labels = self.get_label(metric.metric, r[i], slot_descr)
            yield gen, self.type, self.scale, *labels
