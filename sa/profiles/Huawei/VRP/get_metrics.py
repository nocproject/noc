# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Huawei.VRP.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"



class SlotRule(OIDRule):

    name = "slot"

    def iter_oids(self, script, metric):

        hwFrameIndex = [0]
        hwSlotIndex = [0]
        hwCpuDevIndex = [0]

        if script.has_capability("Stack | Members"):
            hwSlotIndex = range(0, script.capabilities["Stack | Members"])
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
                if gen:
                    yield tuple(gen), self.type, self.scale, {"slot": i}
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                if oid:
                    yield oid, self.type, self.scale, {"slot": i}
