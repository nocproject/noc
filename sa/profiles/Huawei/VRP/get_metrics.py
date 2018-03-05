# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.sa.profiles.Generic.get_metrics import OIDRule
from noc.core.mib import mib


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    ALL_IFACE_METRICS = set(["Interface | Errors | CRC", "Interface | Errors | Frame"])

    def collect_profile_metrics(self, metrics):
        if self.has_capability("DB | Interfaces"):
            self.logger.debug("Merics %s" % metrics)
            if self.ALL_IFACE_METRICS.intersection(set(m.metric for m in metrics)):
                # check
                self.collect_iface_metrics(metrics)

    def collect_iface_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #    return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_iface_metrics()
        self.logger.debug("Metrics: %s", m)
        for bv in metrics:
            if bv.metric in self.ALL_IFACE_METRICS:
                id = tuple(bv.path + [bv.metric])
                if id in m:
                    print(id)
                    self.set_metric(
                        id=bv.id,
                        metric=bv.metric,
                        value=m[id],
                        ts=ts,
                        path=bv.path,
                    )

    def get_iface_metrics(self):
        r = {}
        v = self.cli("display interface")
        v = self.profile.parse_ifaces(v)
        metric_map = {"CRC": "Interface | Errors | CRC",
                      "Frames": "Interface | Errors | Frame"}
        for iface in v:
            for m in metric_map:
                if m not in v[iface]:
                    continue
                r[("", "", "", self.profile.convert_interface_name(iface), metric_map[m])] = int(v[iface][m])
        return r


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
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                if gen:
                    yield tuple(gen), self.type, self.scale, path
            else:
                oid = mib[self.expand(self.oid, {"hwSlotIndex": r[i]})]
                path = ["0", "0", i, ""] if "CPU" in metric.metric else ["0", i, "0"]
                if oid:
                    yield oid, self.type, self.scale, path


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
                    path = ["0", si, cp]
                    if gen:
                        yield tuple(gen), self.type, self.scale, path
                else:
                    oid = mib[self.expand(self.oid, {"hwSlotIndex": r[(si, cp)]})]
                    path = ["0", si, cp]
                    if oid:
                        yield oid, self.type, self.scale, path
