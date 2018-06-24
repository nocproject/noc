# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_mpls_vpn"
    interface = IGetMPLSVPN

    requires = []

    def execute_snmp(self):
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        r = {}
        for conf_id, vrf_vpn_id, vrf_rd, vrf_descr, vrf_oper in self.snmp.get_tables(
                [mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfVpnId"],
                 mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRD"],
                 mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfDescription"],
                 mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfOperStatus"]]):
            vrf_name = "".join([chr(int(x)) for x in conf_id.split(".")[1:]])
            r[conf_id] = {
                "type": "VRF",
                "status": vrf_oper,
                "vpn_id": vrf_vpn_id or "",
                "name": vrf_name,
                "rd": vrf_rd,
                "rt_export": [],
                "rt_import": [],
                "description": vrf_descr,
                "interfaces": []
            }
        for conf_id, row_status in self.snmp.get_tables(
                [mib["MPLS-L3VPN-STD-MIB::mplsL3VpnIfConfRowStatus"]]):
            conf_id, ifindex = conf_id.rsplit(".", 1)
            r[conf_id]["interfaces"] += [names[int(ifindex)]]
        for conf_id, vrf_rt, vrf_rt_decr in self.snmp.get_tables([
            mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRT"],
            mib["MPLS-L3VPN-STD-MIB::mplsL3VpnVrfRTDescr"]
        ]):
            # rt_type: import(1), export(2), both(3)
            conf_id, rt_index, rt_type = conf_id.rsplit(".", 2)
            if rt_type in {"2", "3"}:
                r[conf_id]["rt_export"] += [vrf_rt]
            if rt_type in {"1", "3"}:
                r[conf_id]["rt_import"] += [vrf_rt]
        return list(six.itervalues(r))
