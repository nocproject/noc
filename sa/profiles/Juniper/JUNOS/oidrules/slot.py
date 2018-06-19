# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.SlotRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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
            if "PIC" in desc or "MIC" in desc or "Routing Engine" in desc or "FPC" in desc:
                slotid = i[len("1.3.6.1.4.1.2636.3.1.13.1.5") + 1:]
                oid = mib[self.expand(self.oid, {"hwSlotIndex": slotid})]
                path = ["0", "0", "0", desc] if "CPU" in metric.metric else ["0", "", desc]
                if oid:
                    yield oid, self.type, self.scale, path
