# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSN.hiX56xx.get_mac_address_table
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_port = re.compile(
        r"^\s*(?P<port>\d+/\d+)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<admin_status>Up|Dwn|-)/(?P<oper_status>Up|Dwn)",
        re.MULTILINE,
    )
    rx_port_name = re.compile(r"^\s+ifName\s+(?P<ifname>\S+)\s*\n", re.MULTILINE)
    rx_line = re.compile(
        r"^(?P<interfaces>\d+/\d+(?:/\d+)?)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<mac>\S+)\s+(\S+)\s+(?P<type>\S+)\s+",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac"
        reset = ""
        port_map = {}
        if mac is not None:
            reset += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            reset += " port %s" % interface
        if vlan is not None:
            reset += " vlan %s" % vlan
        if not reset:
            ports = []
            # Do not use range s1-s10 due to high CPU utilization
            v = self.cli("show port", cached=True)  # used in get_interfaces
            for match in self.rx_port.finditer(v):
                ifname = match.group("port")
                ports += [ifname]
                v1 = self.cli(
                    "show port statistics interface %s" % ifname,
                    cached=True,  # used in get_interfaces
                )
                match1 = self.rx_port_name.search(v1)
                port_map[ifname] = match1.group("ifname")
            reset = " port %s-%s" % (ports[0], ports[-1])
        cmd = cmd + reset
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            # Not supported at all
            raise self.NotSupportedError()

        r = []
        for match in self.rx_line.finditer(macs):
            ifname = match.group("interfaces")
            # Set interface's name according to ifName
            if ifname in port_map:
                ifname = port_map[ifname]
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [ifname],
                    "type": {"dynamic": "D", "static": "S", "p-locked": "S"}[
                        match.group("type").lower()
                    ],
                }
            ]

        return r
