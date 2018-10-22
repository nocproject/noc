# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alcatel.7302.SlotRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib


class SlotRule(OIDRule):

    name = "slot"

    def iter_oids(self, script, metric):
        i = 4353
        # 4353 - nt-a slot num
        # chassis, slot, module, name
        r = {}
        if script.has_capability("Stack | Member Ids"):
            sys_slot_index = [0] + [int(index) for index in script.capabilities["Stack | Member Ids"].split(" | ")]
        elif script.has_capability("Stack | Members"):
            sys_slot_index = [0] + range(1, script.capabilities["Stack | Members"] + 1)
        else:
            sys_slot_index = [0]

        for ms in sys_slot_index:
            if ms in [0]:
                # nt-a card - 3 sensors
                for s_i in range(1, 5):
                    # r["nt-a_s%d" % s_i] = "%d.%d" % (ms, s_i)
                    r[("1", "1", "0", "Temperature_nt-a_s%d" % s_i, )] = "%d.%d" % (ms, s_i)
                continue
            # r[str(i)] = {"healthModuleSlot": ms}
            for s_i in range(1, 3):
                # Two sensors on cards
                # r["lt:1/1/%d_s%d" % (ms, s_i)] = "%d.%d" % (i + ms - 2 if ms not in [2, 3] else i + 8 + ms, s_i)
                r[("1", "1", str(ms),
                   "Temperature_lt_s%d" % s_i, )] = "%d.%d" % (i + ms - 2 if ms not in [2, 3] else i + 8 + ms, s_i)

        for i in r:
            if self.is_complex:
                gen = [mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid]
                if gen:
                    yield tuple(gen), self.type, self.scale, list(i)
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                if oid:
                    yield oid, self.type, self.scale, list(i)
