# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from noc.core.text import parse_table


class Script(GetMetricsScript):
    name = "Juniper.JUNOSe.get_metrics"
    OID_RULES = [SlotRule]

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPTP",
        volatile=False,
        access=None,  # CLI version
    )
    def get_subscribers_metrics(self, metrics):
        """
        Returns collected subscribers metric in form
        slot id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        v = self.cli("show subscribers summary slot")
        v = v.splitlines()[:-2]
        v = "\n".join(v)
        r_v = parse_table(v)
        if len(r_v) >= 3:
            for slot, rtt in six.iteritems(r_v):
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    path=("0", str(slot), ""),
                    value=int(rtt),
                    multi=True,
                )
