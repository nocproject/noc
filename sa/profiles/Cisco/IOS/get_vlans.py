# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Cisco.IOS.get_vlans"
    implements = [IGetVlans]

    ##
    ## Extract vlan information
    ##
    rx_vlan_line = re.compile(
        r"^(?P<vlan_id>\d{1,4})\s+(?P<name>.+?)\s+(?:active|act/lshut)",
        re.MULTILINE)

    def extract_vlans(self, data):
        return [
            {
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
            }
            for match in self.rx_vlan_line.finditer(data)
        ]

    ##
    ## Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
    ##
    rx_vlan_ubr = re.compile(
        r"^(\S+\s+){4}(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)", re.MULTILINE)

    @NOCScript.match(version__contains="BC")
    def execute_ubr(self):
        vlans = self.cli("show running-config | include cable dot1q-vc-map")
        r = []
        for match in self.rx_vlan_ubr.finditer(vlans):
            r += [{
                "vlan_id": int(match.group("vlan_id")),
                 "name": match.group("name")
            }]
        return r

    ##
    ## 18xx/28xx/36xx/37xx/38xx/72xx/73xx/75xx/107xx with EtherSwitch module;
    ## C17xx, C18XX, C26xx, C29xx, C39xx, C8xx series
    ##
    rx_vlan_dot1q = re.compile(
        r"^Total statistics for 802.1Q VLAN (?P<vlan_id>\d{1,4}):",
        re.MULTILINE)

    @NOCScript.match(platform__regex=r"^([123][678]\d\d|7[235]\d\d|107\d\d|"
        r"C[23][69]00[a-z]?$|C8[75]0|C1700|C18[01]X|C1900|C2951|ASR\d+)")

    def execute_vlan_switch(self):
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
                r += [{
                    "vlan_id": vlan_id
                }]
            return r
        vlans, _ = vlans.split("\nVLAN Type", 1)
        return self.extract_vlans(vlans)

    rx_5350_vlans = re.compile(
        r"^Virtual LAN ID: \s+(?P<vlan_id>\d{1,4})",
        re.MULTILINE)

    # Cisco 5350/5350XM:
    @NOCScript.match(platform__regex=r"^5350")
    def execute_vlans(self):
        r = []
        try:
            vlans = self.cli("show vlans")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_5350_vlans.finditer(vlans):
            vlan_id = int(match.group("vlan_id"))
            r += [{
                "vlan_id": vlan_id
            }]
        return r

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_vlan_brief(self):
        vlans = self.cli("show vlan brief")
        return self.extract_vlans(vlans)
