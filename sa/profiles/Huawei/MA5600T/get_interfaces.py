# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240

    rx_if1 = re.compile(
        r"^\s*(?P<ifname>[a-zA-Z]+)(?P<ifnum>\d+) current state :\s*(?P<admin_status>UP|DOWN)\s*\n"
        r"^\s*Line protocol current state :\s*(?P<oper_status>UP|UP \(spoofing\)|DOWN)\s*\n"
        r"^\s*Description :\s*(?P<descr>.*)\n"
        r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"(^\s*Forward plane MTU: \S+\n)?"
        r"(^\s*Internet Address is (?P<ip>\S+)\s*\n)?"
        r"(^\s*IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is (?P<mac>\S+)\s*\n)?",
        re.MULTILINE)
    rx_if2 = re.compile(
        r"^Description : (?P<descr>HUAWEI, SmartAX Series), (?P<ifname>[a-zA-Z]+)(?P<ifnum>\d+) Interface\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"(^Internet Address is (?P<ip>\S+)\s*\n)?"
        r"(^IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is (?P<mac>\S+)\s*\n)?"
        r"(^MEth port is (?P<ifparent>\S+)\s*\n)?",
        re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*\-+\s*\n"
        r"(?P<tagged>.+)"
        r"^\s*\-+\s*\n"
        r"^\s*Total:\s+\d+\s+Native VLAN:\s+(?P<untagged>\d+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_vlan2 = re.compile(
        r"^\s+\d+\s+eth\s+(?:down|up)\s+(?P<ifname>\d+/\s*\d+/\s*\d+)\s+"
        r"vlan\s+(?P<type>\S+)\s*\n",
        re.MULTILINE)
    rx_ether = re.compile(
        r"^\s*(?P<port>\d+)\s+(?:10)?[GF]E\s+(\S+\s+)?(\d+\s+)?(\S+\s+)?\S+\s+\S+\s+\S+\s+"
        r"\S+\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s*\n",
        re.MULTILINE)
    rx_adsl_state = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<oper_state>\S+)", re.MULTILINE)
    rx_pvc = re.compile(
        r"^\s*\d+\s+p2p\s+lan\s+[0\*]/(?:\d+|\*)\s*/(?P<vlan>(?:\d+|\*))\s+\S*\s+\S+\s+\S+\s+"
        r"adl\s+0/\d+\s*/(?P<port>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\d+\s+"
        r"(?P<admin_status>\S+)\s*\n", re.MULTILINE)
    rx_sp = re.compile(
        r"^\s*\d+\s+(?P<vlan>\d+)\s+\S+\s+(:?adl|vdl||gpon)\s+0/\d+\s*/(?P<port>\d+)\s+"
        r"(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\S+\s+\S+\s+(?:\d+|\-)\s+(?:\d+|\-)\s+"
        r"(?P<admin_status>up|down)\s*$", re.MULTILINE)
    rx_stp = re.compile(
        r"^\s*\d+\s+(?P<port>0/\s*\d+/\s*\d+)\s+\d+\s+\d+\s+Enabled\s+",
        re.MULTILINE)

    type = {
        "Vlan": 48,
        "GPON": 125,
        "EPON": 126,
        "TDME1": 97,
        "ATM": 4,
        "ADSL": 6,
        "VDSL2": 124,
        "SHDSL": 44,
        "Eth": 7,
        "IMA": 39,
        "IMALink": 51,
        "Trunk": 54,
        "BITS": 96,
        "xDSLchan": 123,
        "DOCSISup": 59,
        "DOCSISdown": 60,
        "DOCSISport": 61
    }

    def snmp_index(self, int_type, shelfID, slotID, intNum):
        """
        Huawei MA5600T&MA5603T port -> ifindex converter
        """

        type_id = self.type[int_type]
        index = type_id << 25
        index += shelfID << 19
        index += slotID << 13
        if int_type in ["Vlan"]:
            index += intNum
        elif int_type in ["xDSLchan", "DOCSISup", "DOCSISdown"]:
            index += intNum << 5
        else:
            index += intNum << 6

        return index

    def get_stp(self):
        r = []
        for match in self.rx_stp.finditer(self.cli("display stp\r\n")):
            port = match.group("port").replace(" ", "")
            if port not in r:
                r += [port]
        return r

    def execute(self):
        interfaces = []
        stp_ports = self.get_stp()
        display_pvc = False
        display_service_port = False
        vlans_found = False
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
            iface = {
                "name": pc["interface"],
                "type": "aggregated",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [{
                    "name": pc["interface"],
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["BRIDGE"]
                }]
            }
            interfaces += [iface]
        ports = self.profile.fill_ports(self)
        for i in range(len(ports)):
            if ports[i]["t"] in ["10GE", "GE", "FE"]:
                v = self.cli("display board 0/%d" % i)
                for match in self.rx_ether.finditer(v):
                    ifname = "0/%d/%d" % (i, int(match.group("port")))
                    admin_status = match.group("admin_status") == "active"
                    oper_status = match.group("oper_status") == "online"
                    ifindex = self.snmp_index("Eth", 0, i, int(match.group("port")))
                    iface = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "snmp_ifindex": ifindex,
                        "enabled_protocols": [],
                        "subinterfaces": [{
                            "name": ifname,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "enabled_afi": ["BRIDGE"]
                        }]
                    }
                    if ifname in stp_ports:
                        iface["enabled_protocols"] += ["STP"]
                    if ifname in portchannel_members:
                        ai, is_lacp = portchannel_members[ifname]
                        iface["aggregated_interface"] = ai
                        iface["enabled_protocols"] += ["LACP"]
                    v = self.cli("display port vlan %s" % ifname)
                    m = self.rx_vlan.search(v)
                    if m:
                        vlans_found = True
                        tagged = []
                        untagged = int(m.group("untagged"))
                        for t in self.rx_tagged.finditer(m.group("tagged")):
                            if int(t.group("tagged")) != untagged:
                                tagged += [int(t.group("tagged"))]
                        iface["subinterfaces"][0]["untagged"] = untagged
                        iface["subinterfaces"][0]["tagged"] = tagged
                    interfaces += [iface]
            if ports[i]["t"] in ["ADSL", "VDSL", "GPON"]:
                oper_states = []
                if ports[i]["t"] == "VDSL":
                    p_type = "vdsl"
                else:
                    p_type = "adsl"
                try:
                    v = self.cli("display %s port state 0/%d\r\n" % (p_type, i))
                    for match in self.rx_adsl_state.finditer(v):
                        oper_states += [{
                            "name": "0/%d/%d" % (i, int(match.group("port"))),
                            "oper_state": match.group("oper_state") == "Activated"
                        }]
                except self.CLISyntaxError:
                    pass
                if (not display_pvc) and (not display_service_port):
                    try:
                        self.cli("display pvc number")
                        display_pvc = True
                    except self.CLISyntaxError:
                        display_service_port = True
                if display_pvc:
                    v = self.cli("display pvc 0/%d\n" % i)
                    rx_adsl = self.rx_pvc
                elif display_service_port:
                    v = self.cli("display service-port board 0/%d\n" % i)
                    rx_adsl = self.rx_sp
                else:
                    v = ""
                    rx_adsl = ""
                for match in rx_adsl.finditer(v):
                    port = int(match.group("port"))
                    ifname = "0/%d/%d" % (i, port)
                    sub = {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "up",
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "vpi": int(match.group("vpi")),
                        "vci": int(match.group("vci"))
                    }
                    if match.group("vlan") != "*":
                        sub["vlan_ids"] = int(match.group("vlan"))
                    found = False
                    for iface in interfaces:
                        if ifname == iface["name"]:
                            if "vlan_ids" in sub:
                                sub["name"] = "%s.%d" % (sub["name"], sub["vlan_ids"])
                            iface["subinterfaces"] += [sub]
                            found = True
                            break
                    if not found:
                        if ports[i]["t"] == "VDSL":
                            ifindex = self.snmp_index("VDSL2", 0, i, port)
                        else:
                            ifindex = self.snmp_index(ports[i]["t"], 0, i, port)
                        if "vlan_ids" in sub:
                            sub["name"] = "%s.%d" % (sub["name"], sub["vlan_ids"])
                        iface = {
                            "name": ifname,
                            "type": "physical",
                            "snmp_ifindex": ifindex,
                            "subinterfaces": [sub]
                        }
                        for o in oper_states:
                            if ifname == o["name"]:
                                iface["oper_status"] = o["oper_state"]
                                break
                        interfaces += [iface]
        v = self.cli("display interface\n")
        rx = self.find_re([self.rx_if1, self.rx_if2], v)
        for match in rx.finditer(v):
            ifname = "%s%s" % (match.group("ifname"), match.group("ifnum"))
            iftype = {
                "meth": "management",
                "null": "null",
                "loopback": "loopback",
                "vlanif": "SVI"
            }[match.group("ifname").lower()]
            iface = {
                "name": ifname,
                "type": iftype,
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "mtu": int(match.group("mtu"))
            }
            if "admin_status" in match.groupdict():
                iface["admin_status"] = match.group("admin_status") != "DOWN"
                sub["admin_status"] = match.group("admin_status") != "DOWN"
            if "oper_status"  in match.groupdict():
                iface["oper_status"] = match.group("oper_status") != "DOWN"
                sub["oper_status"] = match.group("oper_status") != "DOWN"
            if match.group("descr"):
                if match.group("descr") != 'HUAWEI, SmartAX Series':
                    iface["description"] = match.group("descr")
                    sub["description"] = match.group("descr")
            if match.group("ip"):
                sub["ipv4_addresses"] = [match.group("ip")]
                sub["enabled_afi"] = ['IPv4']
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("ifname") == "vlanif":
                sub["vlan_ids"] = int(match.group("ifnum"))
            if "ifparent" in match.groupdict() and match.group("ifparent"):
                for i in interfaces:
                    if i["name"] == match.group("ifparent"):
                        i["subinterfaces"] += [sub]
                        break
            else:
                iface["subinterfaces"] += [sub]
                interfaces += [iface]
        if not vlans_found:
            for vlan in self.scripts.get_vlans():
                for match in self.rx_vlan2.finditer(
                    self.cli("display vlan %s\n" % vlan["vlan_id"])
                ):
                    ifname = match.group("ifname").replace(" ", "")
                    for i in interfaces:
                        if ifname == i["name"]:
                            if match.group("type") == "untag":
                                i["subinterfaces"][0]["untagged_vlan"] = \
                                    vlan["vlan_id"]
                            else:
                                if "tagged_vlans" in i["subinterfaces"][0]:
                                    i["subinterfaces"][0]["tagged_vlans"] += \
                                        [vlan["vlan_id"]]
                                else:
                                    i["subinterfaces"][0]["tagged_vlans"] = \
                                        [vlan["vlan_id"]]
                            break
        return [{"interfaces": interfaces}]
