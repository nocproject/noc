# ---------------------------------------------------------------------
# Cisco.IOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.IOS.get_vlans"
    interface = IGetVlans

    #
    # Extract vlan information
    #
    rx_vlan_line = re.compile(
        r"^(?P<vlan_id>\d{1,4})\s+(?P<name>.+?)\s+(?:active|act/lshut)", re.MULTILINE
    )

    def extract_vlans(self, data):
        return [
            {"vlan_id": int(match.group("vlan_id")), "name": match.group("name")}
            for match in self.rx_vlan_line.finditer(data)
        ]

    rx_vlan_ubr = re.compile(r"^(\S+\s+){4}(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)", re.MULTILINE)

    def execute_ubr(self):
        """
        Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
        :return:
        """
        vlans = self.cli("show running-config | include cable dot1q-vc-map")
        r = []
        for match in self.rx_vlan_ubr.finditer(vlans):
            r += [{"vlan_id": int(match.group("vlan_id")), "name": match.group("name")}]
        return r

    rx_vlan_dot1q = re.compile(
        r"^Total statistics for 802.1Q VLAN (?P<vlan_id>\d{1,4}):", re.MULTILINE
    )

    def execute_vlan_switch(self):
        """
        18xx/28xx/36xx/37xx/38xx/72xx/73xx/75xx/107xx with EtherSwitch module;
        C17xx, C18XX, C26xx, C29xx, C39xx, C8xx series

        :return:
        """
        try:
            vlans = self.cli("show vlan-switch")
        except self.CLISyntaxError:
            try:
                vlans = self.cli("show vlans dot1q")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
            r = []
            for match in self.rx_vlan_dot1q.finditer(vlans):
                vlan_id = int(match.group("vlan_id"))
                r += [{"vlan_id": vlan_id}]
            return r
        vlans, _ = vlans.split("\nVLAN Type", 1)
        return self.extract_vlans(vlans)

    rx_5350_vlans = re.compile(r"^Virtual LAN ID: \s+(?P<vlan_id>\d{1,4})", re.MULTILINE)

    def execute_vlans(self):
        # Cisco 5350/5350XM:
        r = []
        try:
            vlans = self.cli("show vlans")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_5350_vlans.finditer(vlans):
            vlan_id = int(match.group("vlan_id"))
            r += [{"vlan_id": vlan_id}]
        return r

    #
    #  Other
    #
    def execute_cli(self, **kwargs):
        if self.is_5350:
            return self.execute_vlans()
        if self.is_vlan_switch:
            return self.execute_vlan_switch()
        if self.is_ubr:
            return self.execute_ubr()
        vlans = None
        for cmd in ("show vlan brief", "show vlan-switch brief"):
            try:
                vlans = self.cli(cmd)
                break
            except self.CLISyntaxError:
                continue
        if vlans:
            return self.extract_vlans(vlans)
        raise self.NotSupportedError

    def execute_snmp(self, **kwargs):
        r = []
        for vlan_index, vlan_state, vlan_name in self.snmp.get_tables(
            [mib["CISCO-VTP-MIB::vtpVlanState"], mib["CISCO-VTP-MIB::vtpVlanName"]]
        ):
            # print port_num, ifindex, port_type, pvid
            domain_id, vlan_id = vlan_index.split(".")
            r += [{"vlan_id": vlan_id, "name": vlan_name}]
        return r
