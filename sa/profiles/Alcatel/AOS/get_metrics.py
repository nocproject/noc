# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.mib import mib
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Alcatel.AOS.get_metrics"


class SlotRule(OIDRule):
    name = "slot"

    def iter_oids(self, script, metric):
        health_module_slot = [0]
        i = 1
        r = {}

        if script.has_capability("Stack | Members"):
            health_module_slot = range(1, script.capabilities["Stack | Members"] + 1)

        for ms in health_module_slot:
            r[str(i)] = "%d" % ms
            # r[str(i)] = {"healthModuleSlot": ms}
            i += 1

        for i in r:
            if self.is_complex:
                gen = [mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid]
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                if gen:
                    yield tuple(gen), self.type, self.scale, path
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                if oid:
                    yield oid, self.type, self.scale, path
