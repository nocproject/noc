# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_cont = re.compile(r",\s*$\s+", re.MULTILINE)
    rx_line = re.compile(r"\n+\s*Name:\s+", re.MULTILINE)
    rx_body = re.compile(
        r"^(?P<interface>\S+).+"
        r"^\s*Administrative Mode: (?P<amode>.+).+"
        r"^\s*Operational Mode: (?P<omode>.+).+"
        r"^\s*Administrative Trunking Encapsulation:.+"
        r"^\s*Access Mode VLAN: (?P<avlan>\d+) \(.+\).+"
        r"^\s*Trunking Native Mode VLAN: (?P<nvlan>\d+) \(.+\).+"
        r"^\s*Trunking VLANs Enabled: (?P<vlans>.+?)$",
        # "Pruning VLANs Enabled:",
        re.MULTILINE | re.DOTALL,
    )

    rx_descr_if = re.compile(
        r"^(?P<interface>\S+)\s+(?:up|down|admin down|deleted)\s+"
        r"(?:up|down)\s+(?P<description>.+)"
    )
    rx_tagged = re.compile(
        r"^Port\s+Vlans allowed on trunk\s*\n^\S+\s+([0-9\-\,]+)\s*\n", re.MULTILINE
    )

    rx_conf_iface = re.compile(
        r"^\s*interface (?P<ifname>\S+)\s*\n"
        r"(^\s*description (?P<descr>.+?)\n)?"
        r"(^\s*switchport trunk native vlan (?P<untagged>\d+)\s*\n)?"
        r"^\s*switchport trunk encapsulation dot1q\s*\n"
        r"^\s*switchport trunk allowed vlan (?P<vlans>.+?)"
        r"^\s*switchport mode (?P<mode>trunk|access)",
        re.MULTILINE | re.DOTALL,
    )

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
        for ifindex, port_type, pvid, port_status in self.snmp.get_tables(
            [
                mib["CISCO-VLAN-MEMBERSHIP-MIB::vmVlanType"],
                mib["CISCO-VLAN-MEMBERSHIP-MIB::vmVlan"],
                mib["CISCO-VLAN-MEMBERSHIP-MIB::vmPortStatus"],
            ]
        ):
            # print port_num, ifindex, port_type, pvid
            r[int(ifindex)] = {
                "interface": names[int(ifindex)],
                "status": port_status == 2,
                # "ifindex": ifindex,
                # "port_type": port_type,
                "untagged": pvid,
                "tagged": [],
                "members": [],
            }
        start = 0
        for (
            ifindex,
            native_vlan,
            enc_type,
            vlans_base,
            vlans_2k,
            vlans_3k,
            vlans_4k,
        ) in self.snmp.get_tables(
            [
                mib["CISCO-VTP-MIB::vlanTrunkPortNativeVlan"],
                mib["CISCO-VTP-MIB::vlanTrunkPortEncapsulationOperType"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled2k"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled3k"],
                # mib["CISCO-VTP-MIB::vlanTrunkPortVlansEnabled4k"]
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined2k"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined3k"],
                mib["CISCO-VTP-MIB::vlanTrunkPortVlansXmitJoined4k"],
            ]
        ):
            # print(ifindex, enc_type, vlans_base, vlans_2k, vlans_3k, vlans_4k)
            if int(enc_type) != 4:
                # not dot1Q
                continue
            vlans_bank = hexlify("".join([vlans_base, vlans_2k, vlans_3k, vlans_4k]))
            # vlans_bank = hexlify(vlans_bank)
            if int(ifindex) in r:
                r[int(ifindex)]["tagged"] += list(
                    compress(range(start, 4096), self.convert_vlan(vlans_bank))
                )
            else:
                r[int(ifindex)] = {
                    "interface": names[int(ifindex)],
                    "status": True,
                    # "ifindex": ifindex,
                    # "port_type": port_type,
                    "untagged": native_vlan,
                    "tagged": list(compress(range(start, 4096), self.convert_vlan(vlans_bank))),
                    "members": [],
                }
            # r[port_num]["802.1Q Enabled"] = True
        return list(six.itervalues(r))

    def parse_config(self):
        r = []
        c = self.scripts.get_config()
        for match in self.rx_conf_iface.finditer(c):
            vlans = match.group("vlans").replace("switchport trunk allowed vlan add", ",")
            iface = {
                "interface": match.group("ifname"),
                "tagged": self.expand_rangelist(vlans),
                "members": [],
                "802.1Q Enabled": True,
                "802.1ad Tunnel": False,
            }
            if match.group("untagged"):
                iface["untagged"] = match.group("untagged")
            if match.group("descr"):
                iface["description"] = match.group("descr")
            r += [iface]
        return r

    def get_description(self):
        r = []
        s = self.cli("show interfaces description", cached=True)
        for l in s.split("\n"):
            match = self.rx_descr_if.match(l.strip())
            if not match:
                continue
            r += [
                {
                    "interface": self.profile.convert_interface_name(match.group("interface")),
                    "description": match.group("description"),
                }
            ]
        return r

    def execute_cli(self, **kwargs):
        r = []
        try:
            v = self.cli("show interfaces switchport")
        except self.CLISyntaxError:
            # Cisco Catalist 3500 XL do not have this command
            # raise self.NotSupportedError()
            return self.parse_config()
        v = "\n" + v
        v = self.rx_cont.sub(",", v)  # Unwind continuation lines
        # Get portchannel members
        portchannels = {}  # portchannel name -> [members]
        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]
        # Get descriptions
        descriptions = {}  # interface name -> description
        for p in self.get_description():
            descriptions[p["interface"]] = p["description"]
        # Get vlans
        known_vlans = {vlan["vlan_id"] for vlan in self.scripts.get_vlans()}
        # For each interface
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_body.search(s)
            if not match:
                continue  # raise self.NotSupportedError()

            interface = self.profile.convert_interface_name(match.group("interface"))
            is_trunk = match.group("amode").strip() == "trunk"

            if is_trunk:
                untagged = int(match.group("nvlan"))
                vlans = match.group("vlans").strip()
                if vlans == "ALL":
                    tagged = list(range(1, 4095))
                elif vlans.upper() == "NONE":
                    tagged = []
                #
                # Cisco hides info like this
                # 3460,3463-3467,3469-3507,3512,3514,3516-3519,3528,(more)
                #
                elif "more" in vlans:
                    try:
                        c = self.cli("show interface %s trunk" % interface)
                        match1 = self.rx_tagged.search(c)
                        if match1:  # If not `none` in returned list
                            tagged = self.expand_rangelist(match1.group(1))
                    except self.CLISyntaxError:
                        # Return anything
                        tagged = self.expand_rangelist(vlans[:-7])
                else:
                    tagged = self.expand_rangelist(vlans)
                if untagged in tagged:
                    # Exclude native vlan from tagged
                    tagged.remove(untagged)
            else:
                untagged = int(match.group("avlan"))
                tagged = []

            iface = {
                "interface": interface,
                "status": match.group("omode").strip() != "down",
                "tagged": [vlan for vlan in tagged if vlan in known_vlans],
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": False,
            }
            if untagged:
                iface["untagged"] = untagged
            if interface in descriptions:
                iface["description"] = descriptions[interface]

            r += [iface]
        return r
