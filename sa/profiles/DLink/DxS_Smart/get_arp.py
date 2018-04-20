# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_arp"
    interface = IGetARP
=======
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True
    rx_line = re.compile(
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+"
        r"ARPA\s+(?P<interface>\S+)\s+\S+", re.MULTILINE)
    rx_line1 = re.compile(
        r"^(?P<interface>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+(?:Static|Dynamic)", re.MULTILINE)

    def execute(self):
        r = []
<<<<<<< HEAD
        if self.has_snmp():
            try:
                mac_ip = {}
                for mac, ip in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.2",
                    "1.3.6.1.2.1.4.22.1.3", cached=True):  # IP-MIB
                    mac = ":".join(["%02x" % ord(c) for c in mac])
                    #ip = ["%02x" % ord(c) for c in ip]
                    #mac_ip[mac] = ".".join(str(int(c, 16)) for c in ip)
                    mac_ip[mac] = ip
                for i, mac in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.1",
                    "1.3.6.1.2.1.4.22.1.2", cached=True):  # IP-MIB
                    mac = ":".join(["%02x" % ord(c) for c in mac])
                    interface = self.snmp.get("1.3.6.1.2.1.2.2.1.1." + str(i),
                        cached=True)  # IF-MIB
                    try:
                        r.append({"ip": mac_ip[mac],
                            "mac": mac,
                            "interface": interface,
                            })
                    except KeyError:
                        pass
=======

        # BUG http://bt.nocproject.org/browse/NOC-36
        # Only one way: SNMP.
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for ip, mac, i in self.snmp.join_tables("1.3.6.1.2.1.4.22.1.3",
                                                        "1.3.6.1.2.1.4.22.1.2",
                                                        "1.3.6.1.2.1.4.22.1.1",
                                                        bulk=True,
                                                        cached=True):  # IP-MIB
                    r += [{"ip": ip, "mac": mac, "interface": self.snmp.get(
                        "1.3.6.1.2.1.2.2.1.2" + '.' + i, cached=True)}]
                return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        r = []
        try:
            s = self.cli("debug info")
            for match in self.rx_line.finditer(s):
                r += [{
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface"),
                }]
            return r
        except self.CLISyntaxError:
            pass
        s = self.cli("show arpentry")
        for match in self.rx_line1.finditer(s):
            if match.group("mac") != "ff:ff:ff:ff:ff:ff":
                r += [{
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface"),
                }]
        return r
