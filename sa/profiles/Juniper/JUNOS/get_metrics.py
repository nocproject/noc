# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule


class Script(GetMetricsScript):
    name = "Juniper.JUNOS.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(
        ["Subscribers | Summary"],
        #        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if self.is_gte_16:
            for oid, v in self.snmp.getnext("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3", bulk=False):
                oid2 = oid.split("1.3.6.1.4.1.2636.3.64.1.1.1.5.1.3.")
                interf = oid2[1].split(".")
                del interf[0]
                slot = ""
                for x in interf:
                    slot += chr(int(x))
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    path=("0", str(slot), ""),
                    value=int(v),
                    multi=True,
                )
        else:
            metric = self.snmp.get("1.3.6.1.4.1.2636.3.64.1.1.1.2.0")
            self.set_metric(
                id=("Subscribers | Summary", None),
                path=("0", "", ""),
                value=int(metric),
                multi=True,
            )
