# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
import string

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_mpls_vpn"
    interface = IGetMPLSVPN

    requires = []

    # rt_type: import(1), export(2), both(3)
    VRF_TYPE_MAP = {"rt_export": {"2", "3"}, "rt_import": {"1", "3"}}

    def execute_snmp(self):
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        r = {}
        for conf_id, vrf_vpn_id, vrf_rd, vrf_descr, vrf_oper in self.snmp.get_tables(
            [
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfVpnId"],
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRD"],
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfDescription"],
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfOperStatus"],
            ]
        ):
            vrf_name = "".join([chr(int(x)) for x in conf_id.split(".")[1:]])
            r[conf_id] = {
                "type": "VRF",
                "status": vrf_oper,
                "vpn_id": "",
                "name": vrf_name,
                "rd": "".join(x for x in vrf_rd if x in string.printable),
                "rt_export": [],
                "rt_import": [],
                "description": vrf_descr,
                "interfaces": [],
            }
        for conf_id, row_status in self.snmp.get_tables(
            [mib["MPLS-L3VPN-STD-MIB::mplsL3VpnIfConfRowStatus"]]
        ):
            conf_id, ifindex = conf_id.rsplit(".", 1)
            r[conf_id]["interfaces"] += [names[int(ifindex)]]
        for conf_id, vrf_rt, vrf_rt_decr in self.snmp.get_tables(
            [
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRT"],
                mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRTDescr"],
            ]
        ):
            # rt_type: import(1), export(2), both(3)
            vrf_rt = "".join(x for x in vrf_rt if x in string.printable)
            conf_id, rt_index, rt_type = conf_id.rsplit(".", 2)
            if rt_type in self.VRF_TYPE_MAP["rt_export"]:
                r[conf_id]["rt_export"] += [vrf_rt]
            if rt_type in self.VRF_TYPE_MAP["rt_import"]:
                r[conf_id]["rt_import"] += [vrf_rt]
        return list(six.itervalues(r))
