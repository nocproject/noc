# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.SlotRule
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
        """
                SlotNumber
                2 for ERX-3xx models
                6 for ERX-7xx models
                13 for ERX-14xx models
                16 for E320 models
                :param metrics:
                :return:
                """
        juniSystemSlotLevel = [1]
        juniSystemSlotNumber = list(range(0, 17))
        i = 0
        r = {}

        for sn in juniSystemSlotNumber:
            for sl in juniSystemSlotLevel:
                # r[i] = "%d.%d.%d" % (fi, si, cp)
                r[str(i)] = "%d.%d" % (sn, sl)
                # r[str(i)] = {"juniSystemSlotNumber": sn, "juniSystemSlotLevel": sl}
                i += 1

        for i in r:
            if self.is_complex:
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                gen = [mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid]
                if gen:
                    yield tuple(gen), self.type, self.scale, path
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                if oid:
                    yield oid, self.type, self.scale, path
