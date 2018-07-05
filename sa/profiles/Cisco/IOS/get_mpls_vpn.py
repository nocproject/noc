# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_mpls_vpn"
    interface = IGetMPLSVPN
    cache = True

    rx_line = re.compile(r"^\s+(?P<vrf>.+?)\s+"
                         r"(?P<rd>\S+:\S+|<not set>)\s+"
                         "(?P<iface>.*?)\s*$", re.IGNORECASE)
    rx_cont = re.compile("^\s{6,}(?P<iface>.+?)\s*$")
    rx_portchannel = re.compile(r"^Po\s*\d+(?:A|B)?$")

    rx_vrf = re.compile(r"^VRF\s*(?P<vrf>[\S+\s]+?)\s*(\(.+\))?\s*;\s*default\s*RD\s*"
                        r"(?P<rd>\d+:\d+|<not set>);\s*default\s*VPNID\s*(?P<vpnid>\S+|<not set>)")

    portchannel_members = {}

    def _get_portchannel_members(self, iface):
        iface = self.profile.convert_interface_name(iface)
        if not self.portchannel_members:
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                self.portchannel_members[i] = pc["members"]
        if iface in self.portchannel_members:
            return self.portchannel_members[iface]
        else:
            return []

    def execute_cli(self, **kwargs):
        vpns = []
        try:
            v = self.cli("show ip vrf detail")
        except self.CLISyntaxError:
            return self.execute_vrf()
        vrf, rd = None, None
        vrf_block = defaultdict(list)
        block = None
        tab = 100
        for l in v.splitlines():
            # VRF VPN_VRF1 (VRF Id = 00); default RD 65501:4579033191; default VPNID <not set>
            # VRF VPN_VRF1; default RD 65501:4579033191; default VPNID <not set>
            if self.rx_vrf.match(l):
                if vrf and rd:
                    vpns += [{
                        "type": "VRF",
                        "vpn_id": "",
                        "status": True,
                        "name": vrf.strip(),
                        "interfaces": []
                    }]
                    if rd and rd.strip() != '<not set>':
                        vpns[-1]["rd"] = rd.strip()
                    if vrf_block["interfaces:"]:
                        for iface in vrf_block["interfaces:"]:
                            po_match = self.rx_portchannel.match(iface)
                            if po_match:
                                members = self._get_portchannel_members(iface)
                                vpns[-1]["interfaces"] += members
                            else:
                                vpns[-1]["interfaces"] += [iface]
                    if vrf_block["export vpn route-target communities"]:
                        vpns[-1]["rt_export"] = [":".join(lll.split(":")[1:])
                                                 for lll in vrf_block["export vpn route-target communities"]]
                    if vrf_block["import vpn route-target communities"]:
                        vpns[-1]["rt_import"] = [":".join(lll.split(":")[1:])
                                                 for lll in vrf_block["import vpn route-target communities"]]
                vrf, rd, = self.rx_vrf.match(l).group("vrf"), self.rx_vrf.match(l).group("rd")
                # interfaces, vrf_export, vrf_import
                vrf_block = {"interfaces:": [],
                             "export vpn route-target communities": [],
                             "import vpn route-target communities": []}
            elif l.lower().strip() in vrf_block:
                block = l.lower().strip()
                tab = l.count("  ")
            elif not l.strip():
                tab = 100
                block = None
            elif block is not None and l.count("  ") and l.count("  ") > tab:
                vrf_block[block] += l.split()
            elif block is not None and l.count("  ") and l.count("  ") == tab:
                s = []
                for ll in vrf_block[block]:
                    s += [lll.strip() for lll in ll.split() if lll.strip()]
                vrf_block[block] = s[:]
                tab = 100
                block = None
        else:
            if vrf:
                vpns += [{
                    "type": "VRF",
                    "vpn_id": "",
                    "status": True,
                    "name": vrf.strip(),
                    "interfaces": []
                }]
                if rd and rd.strip() != '<not set>':
                    vpns[-1]["rd"] = rd.strip()
                if vrf_block["interfaces:"]:
                    for iface in vrf_block["interfaces:"]:
                        po_match = self.rx_portchannel.match(iface)
                        if po_match:
                            members = self._get_portchannel_members(iface)
                            vpns[-1]["interfaces"] += members
                        else:
                            vpns[-1]["interfaces"] += [iface]
                if vrf_block["export vpn route-target communities"]:
                    vpns[-1]["rt_export"] = [":".join(lll.split(":")[1:])
                                             for lll in vrf_block["export vpn route-target communities"][:] if lll]
                if vrf_block["import vpn route-target communities"]:
                    vpns[-1]["rt_import"] = [":".join(lll.split(":")[1:])
                                             for lll in vrf_block["import vpn route-target communities"][:] if lll]

        return vpns

    def execute_vrf(self, **kwargs):
        vpns = []
        v = self.cli("show ip vrf")
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                iface = match.group("iface").strip()
                if iface:
                    interfaces = [iface]
                    po_match = self.rx_portchannel.match(iface)
                    if po_match:
                        members = self._get_portchannel_members(iface)
                        interfaces += members
                else:
                    interfaces = []
                vpn = {
                    "type": "VRF",
                    "vpn_id": "",
                    "status": True,
                    "name": match.group("vrf"),
                    "interfaces": interfaces
                }
                rd = match.group("rd")
                if ":" in rd:
                    vpn["rd"] = rd
                vpns += [vpn]
            elif vpns:
                match = self.rx_cont.match(l)
                if match:
                    iface = match.group("iface")
                    interfaces = [iface]
                    po_match = self.rx_portchannel.match(iface)
                    if po_match:
                        members = self._get_portchannel_members(iface)
                        interfaces += members
                    vpns[-1]["interfaces"] += interfaces
        return vpns

    def execute_snmp_vrf_mib(self):
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        r = {}
        for vrfindex, vrf_name, vrf_tag, vrf_status in self.snmp.get_tables(
                [
                    mib["CISCO-VRF-MIB::cvVrfName"],
                    mib["CISCO-VRF-MIB::cvVrfVnetTag"],
                    mib["CISCO-VRF-MIB::cvVrfOperStatus"]]):
            # print port_num, ifindex, port_type, pvid
            r[int(vrfindex)] = {
                "type": "VRF",
                "vpn_id": "",
                "status": bool(vrf_status),
                "name": vrf_name.strip(),
                "rd": "0:0",
                "interfaces": []
            }
        for vrfifindex, vrfif_name, vrfif_status in self.snmp.get_tables(
                [mib["CISCO-VRF-MIB::cvVrfInterfaceType"],
                 mib["CISCO-VRF-MIB::cvVrfInterfaceRowStatus"]]):
            vrf_index, ifindex = vrfifindex.split(".")
            r[int(vrf_index)]["interfaces"] += [names[int(ifindex)]]
        return list(six.itervalues(r))

    def execute_snmp_mpls_mib(self):
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        r = {}
        for conf_id, vrf_descr, vrf_rd, vrf_oper in self.snmp.get_tables(
                [mib["MPLS-VPN-MIB::mplsVpnVrfDescription"],
                 mib["MPLS-VPN-MIB::mplsVpnVrfRouteDistinguisher"],
                 mib["MPLS-VPN-MIB::mplsVpnVrfOperStatus"]]):
            vrf_name = "".join([chr(int(x)) for x in conf_id.split(".")[1:]])
            r[conf_id] = {
                "type": "VRF",
                "status": vrf_oper,
                "vpn_id": "",
                "name": vrf_name,
                "rd": vrf_rd,
                "rt_export": [],
                "rt_import": [],
                "description": vrf_descr,
                "interfaces": []
            }
        for conf_id, row_status in self.snmp.get_tables(
                [mib["MPLS-VPN-MIB::mplsVpnInterfaceConfRowStatus"]]):
            conf_id, ifindex = conf_id.rsplit(".", 1)
            r[conf_id]["interfaces"] += [names[int(ifindex)]]
        for conf_id, vrf_rt, vrf_rt_decr in self.snmp.get_tables([
            mib["MPLS-VPN-MIB::mplsVpnVrfRouteTarget"],
            mib["MPLS-VPN-MIB::mplsVpnVrfRouteTargetDescr"]
        ]):
            # rt_type: import(1), export(2), both(3)
            conf_id, rt_index, rt_type = conf_id.rsplit(".", 2)
            if rt_type in {"2", "3"}:
                r[conf_id]["rt_export"] += [vrf_rt]
            if rt_type in {"1", "3"}:
                r[conf_id]["rt_import"] += [vrf_rt]
        return list(six.itervalues(r))

    def execute_snmp(self, **kwargs):
        r = self.execute_snmp_mpls_mib()
        if r:
            return r
        return self.execute_snmp_vrf_mib()
