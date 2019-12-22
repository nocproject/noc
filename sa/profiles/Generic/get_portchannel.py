# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import six
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_portchannel"
    interface = IGetPortchannel
    cache = True
    requires = []

    MAX_GETNEXT_RETIRES = 0

    def execute_snmp(self, **kwargs):
        r = defaultdict(list)
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        for ifindex, sel_pc, att_pc in self.snmp.get_tables(
            [
                mib["IEEE8023-LAG-MIB::dot3adAggPortSelectedAggID"],
                mib["IEEE8023-LAG-MIB::dot3adAggPortAttachedAggID"],
            ]
        ):
            if att_pc:
                if sel_pc > 0:
                    r[names[int(att_pc)]] += [names[int(ifindex)]]
        return [{"interface": pc, "type": "L", "members": r[pc]} for pc in r]
