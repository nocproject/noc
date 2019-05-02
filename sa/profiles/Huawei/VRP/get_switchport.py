# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six
from itertools import compress
from binascii import hexlify
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
from noc.lib.validators import is_int
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.VRP.get_switchport"
    interface = IGetSwitchport

    rx_vlan_comment = re.compile(r"\([^)]+\)", re.MULTILINE | re.DOTALL)
    rx_line1 = re.compile(
        r"(?P<interface>\S+)\s+(?P<mode>access|trunk|hybrid|trunking)\s+(?P<pvid>\d+)\s+(?P<vlans>(?:\d|\-|\s|\n)+)",
        re.MULTILINE)
    rx_line2 = re.compile(
        r"""
        (?P<interface>\S+)\scurrent\sstate
        .*?
        PVID:\s(?P<pvid>\d+)
        .*?
        Port\slink-type:\s(?P<mode>access|trunk|hybrid|trunking)
        .*?
        (?:Tagged\s+VLAN\sID|VLAN\spermitted)?:\s(?P<vlans>.*?)\n
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE)
    rx_descr1 = re.compile(
        r"^(?P<interface>\S+)\s+(?P<description>.+)", re.MULTILINE)
    rx_descr2 = re.compile(
        r"^(?P<interface>\S+)\s+\S+\s+\S+\s+(?P<description>.+)", re.MULTILINE)
    rx_descr3 = re.compile(
        r"^(?P<interface>(?:Eth|GE|TENGE)\d+/\d+/\d+)\s+"
        r"(?P<status>(?:UP|(?:ADM\s)?DOWN))\s+(?P<speed>.+?)\s+"
        r"(?P<duplex>.+?)\s+"
        r"(?P<mode>access|trunk|hybrid|trunking|A|T|H)\s+"
        r"(?P<pvid>\d+)\s*(?P<description>.*)$", re.MULTILINE)
    rx_new_descr = re.compile(
        r"^Interface\s+PHY\s+Protocol\s+Description", re.MULTILINE)

    @staticmethod
    def convert_vlan(vlans):
        """

        :param vlans: Byte string FF 00 01 80 ....
        :return: itera
        """
        for line in vlans.splitlines():
            for vlan_pack in line.split()[0]:
                # for is_v in bin(int(vlan_pack, 16)):
                for is_v in "{0:04b}".format(int(vlan_pack, 16)):
                    yield int(is_v)

    def execute_snmp(self, **kwargs):

        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        r = {}
        for port_num, ifindex, port_type, pvid in self.snmp.get_tables(
                [mib["HUAWEI-L2IF-MIB::hwL2IfPortIfIndex"],
                 mib["HUAWEI-L2IF-MIB::hwL2IfPortType"],
                 mib["HUAWEI-L2IF-MIB::hwL2IfPVID"]]):
            # print port_num, ifindex, port_type, pvid
            r[port_num] = {
                "interface": names[ifindex],
                "status": False,
                # "ifindex": ifindex,
                # "port_type": port_type,
                # "untagged": pvid,
                "tagged": [],
                "members": []
            }
            # Avoid zero-value untagged
            # Found on ME60-X8 5.160 (V600R008C10SPC300)
            if pvid:
                r[port_num]["untagged"] = pvid
        start = 2
        for oid, vlans_bank in self.snmp.get_tables([mib["HUAWEI-L2IF-MIB::hwL2IfTrunkPortTable"]]):
            oid, port_num = oid.rsplit(".", 1)
            vlans_bank = hexlify(vlans_bank)
            if oid == "1.3":
                # HighVLAN
                start = 2048
            # if vlans_bank.startswith("?"):
                # Perhaps 1 vlan
            #    vlans_bank = vlans_bank[1:]
            r[port_num]["tagged"] += list(compress(range(start, 4096), self.convert_vlan(vlans_bank)))
            r[port_num]["802.1Q Enabled"] = True
        # tagged_vlans = list()
        # hybrid_vlans = list(self.snmp.get_tables([mib["HUAWEI-L2IF-MIB::hwL2IfHybridPortTable"]]))

        # x2 = list(compress(range(1, 4096), self.convert_vlan(r2)))
        return list(six.itervalues(r))

    def execute_cli(self, **kwargs):
        # Get descriptions
        descriptions = {}
        try:
            v = self.cli("display interface description")
            if self.rx_new_descr.search(v):
                rx_descr = self.rx_descr2
            else:
                rx_descr = self.rx_descr1
        except self.CLISyntaxError:
            rx_descr = self.rx_descr3
            try:
                v = self.cli("display brief interface")
            except self.CLISyntaxError:
                v = self.cli("display interface brief")

        for match in rx_descr.finditer(v):
            interface = self.profile.convert_interface_name(match.group("interface"))
            description = match.group("description").strip()
            if description.startswith("HUAWEI"):
                description = ""
            if match.group("interface") != "Interface":
                descriptions[interface] = description
        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        # Get portchannel
        portchannels = self.scripts.get_portchannel()

        # Get vlans
        known_vlans = set([vlan["vlan_id"] for vlan in
                           self.scripts.get_vlans()])

        # Get ports in vlans
        r = []
        version = self.profile.fix_version(self.scripts.get_version())
        rx_line = self.rx_line1
        if version.startswith("5.3"):
            v = self.cli("display port allow-vlan")
        elif version.startswith("3.10"):
            rx_line = self.rx_line2
            v = self.cli("display interface")
        else:
            try:
                v = self.cli("display port vlan")
            except self.CLISyntaxError:
                v = "%s\n%s" % (
                    self.cli("display port trunk"),
                    self.cli("display port hybrid")
                )

        for match in rx_line.finditer(v):
            # port = {}
            tagged = []
            trunk = match.group("mode") in ("trunk", "hybrid", "trunking")
            if trunk:
                vlans = match.group("vlans").strip()
                if (
                    vlans and (vlans not in ["-", "none"]) and
                    is_int(vlans[0])
                ):
                    vlans = self.rx_vlan_comment.sub("", vlans)
                    vlans = vlans.replace(" ", ",")
                    tagged = self.expand_rangelist(vlans)
                    # For VRP version 5.3
                    if r and r[-1]["interface"] == match.group("interface"):
                        r[-1]["tagged"] += [x for x in tagged if x in known_vlans]
                        continue
            members = []

            interface = match.group("interface")
            if interface.startswith("Eth-Trunk"):
                ifname = self.profile.convert_interface_name(interface)
                for p in portchannels:
                    if p["interface"] in (ifname, interface):
                        members = p["members"]

            pvid = int(match.group("pvid"))
            # This is an exclusive Chinese networks ?
            if pvid == 0:
                pvid = 1

            port = {
                "interface": interface,
                "status": interface_status.get(interface, False),
                "802.1Q Enabled": trunk,
                "802.1ad Tunnel": False,
                "tagged": [x for x in tagged if x in known_vlans],
                "members": members
            }
            if match.group("mode") in ("access", "hybrid"):
                port["untagged"] = pvid
            description = descriptions.get(interface)
            if description:
                port["description"] = description

            r += [port]
        return r
