# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_metrics
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
from .oidrules.sslot import SSlotRule


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    OID_RULES = [SlotRule, SSlotRule]

    @metrics(
        ["Interface | Errors | CRC", "Interface | Errors | Frame"],
        has_capability="DB | Interfaces",
        volatile=False,
        access="C",  # CLI version
    )
    def get_vrp_interface_metrics(self, metrics):
        v = self.cli("display interface")
        ifdata = self.profile.parse_ifaces(v)
        for iface, data in six.iteritems(ifdata):
            iface = self.profile.convert_interface_name(iface)
            ipath = ["", "", "", iface]
            if "CRC" in data:
                self.set_metric(id=("Interface | Errors | CRC", ipath), value=int(data["CRC"]))
            if "Frames" in data:
                self.set_metric(id=("Interface | Errors | Frame", ipath), value=int(data["Frames"]))
