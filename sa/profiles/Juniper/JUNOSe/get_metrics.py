# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from collections import defaultdict
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent_usage
from noc.lib.text import parse_table


class Script(GetMetricsScript):
    name = "Juniper.JUNOSe.get_metrics"

    SNMP_OIDS = GetMetricsScript.merge_oids({
        "CPU | Usage | 5sec": [
            [
                "SNMP",
                "1.3.6.1.4.1.4874.2.2.2.1.3.5.1.9",
                "gauge", 1, "slot", "%(juniSystemSlotNumber)d.%(juniSystemSlotLevel)d"]],
        "CPU | Load | 1min": [
            [
                "SNMP",
                "1.3.6.1.4.1.4874.2.2.2.1.3.5.1.10",
                "gauge", 1, "slot", "%(juniSystemSlotNumber)d.%(juniSystemSlotLevel)d"]],
        "CPU | Load | 5min": [
            [
                "SNMP",
                "1.3.6.1.4.1.4874.2.2.2.1.3.5.1.11",
                "gauge", 1, "slot", "%(juniSystemSlotNumber)d.%(juniSystemSlotLevel)d"]],
        "Memory | Usage | 5sec": [
            [
                "SNMP",
                "1.3.6.1.4.1.4874.2.2.2.1.3.5.1.4",
                "gauge", 1, "slot", "%(juniSystemSlotNumber)d.%(juniSystemSlotLevel)d"]],
        "Subscribers | IPoE": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.18.1.5.11.0", "counter", 1)
            ],
        "Subscribers | PPP": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.11.1.7.7.0", "counter", 1)
            ],
        "Subscribers | L2TP": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.35.1.1.2.10.0", "gauge", 1)
            ],
        "Environment | Temperature": [
            ("SNMP", "1.3.6.1.4.1.4874.2.2.2.1.9.4.1.3.1", "counter", 1)
            ],
    })

    PROFILE_HINTS = {}

    def collect_profile_metrics(self, metrics):
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
        juniSystemSlotNumber = range(0, 17)
        i = 0
        r = {}
        for sn in juniSystemSlotNumber:
            for sl in juniSystemSlotLevel:
                # r[i] = "%d.%d.%d" % (fi, si, cp)
                r[str(i)] = {"juniSystemSlotNumber": sn, "juniSystemSlotLevel": sl}
                i += 1

        self.PROFILE_HINTS["slot"] = r

        if self.has_capability("BRAS | PPTP"):
            self.collect_subscribers_metrics(metrics)

    def collect_subscribers_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #     return  # NO SLA metrics requested
        if "Subscribers | Summary" in metrics:
            ts = self.get_ts()
            m = self.get_subscribers_metrics()
            for slot in m:
                    self.set_metric(
                        name="Subscribers | Summary",
                        value=m[slot],
                        ts=ts,
                        tags={"slot": slot}
                    )

    def get_subscribers_metrics(self):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        v = self.cli("show subscribers summary slot")
        v = v.splitlines()[:-2]
        v = "\n".join(v)
        r_v = parse_table(v)
        if len(r_v) < 3:
            return {}
        # r = defaultdict(dict)
        r = dict(r_v)
        return r
