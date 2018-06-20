# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.SlotRule
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
        SlotName:
        Routing Engine
        PIC
        FPC
        MIC
        :param metrics:
        :return:
        """
        for i, desc in script.snmp.getnext("1.3.6.1.4.1.2636.3.1.13.1.5"):
            slotid = i[len("1.3.6.1.4.1.2636.3.1.13.1.5") + 1:]
            oid = mib[self.expand(self.oid, {"hwSlotIndex": slotid})]
            if "PIC" in desc or "MIC" in desc:
                path = [int(slotid.split(".")[1]) - 1, int(slotid.split(".")[2]) - 1, int(slotid.split(".")[3]), desc] \
                    if "CPU" in metric.metric or "Environment" in metric.metric \
                    else [int(slotid.split(".")[1]) - 1, int(slotid.split(".")[2]) - 1, desc]
                if oid:
                    yield oid, self.type, self.scale, path
            elif "FPC" in desc:
                path = [int(slotid.split(".")[1]) - 1, slotid.split(".")[2], slotid.split(".")[3], desc] \
                    if "CPU" in metric.metric or "Environment" in metric.metric \
                    else [int(slotid.split(".")[1]) - 1, slotid.split(".")[2], desc]
                if oid:
                    yield oid, self.type, self.scale, path
            elif "Routing Engine" in desc:
                path = [slotid.split(".")[1], slotid.split(".")[2], slotid.split(".")[3], desc] \
                    if "CPU" in metric.metric or "Environment" in metric.metric \
                    else [int(slotid.split(".")[1]), int(slotid.split(".")[2]), desc]
                if oid:
                    yield oid, self.type, self.scale, path
