# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Alcatel.AOS.get_metrics"


class SlotRule(OIDRule):

    name = "slot"

    def iter_oids(self, script, metric):
        healthModuleSlot = [0]
        i = 1
        r = {}

        if script.has_capability("Stack | Members"):
            healthModuleSlot = range(1, script.capabilities["Stack | Members"] + 1)

        for ms in healthModuleSlot:
            r[str(i)] = "%d" % ms
            # r[str(i)] = {"healthModuleSlot": ms}
            i += 1

        for i in r:
            if self.is_complex:
                gen = [mib[self.expand(o, {"hwSlotIndex": r[i]})] for o in self.oid]
                if gen:
                    yield tuple(gen), self.type, self.scale, {"slot": i}
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                if oid:
                    yield oid, self.type, self.scale, {"slot": i}
