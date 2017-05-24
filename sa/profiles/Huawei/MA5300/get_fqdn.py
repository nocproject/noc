# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Huawei.MA5300.get_fqdn"
    interface = IGetFQDN
        

#    rx_ver = re.compile(r"SmartAX (?P<platform>\S+) (?P<version>\S+)")
#    rx_bios = re.compile(r"\s+BIOS Version is\s+(?P<bios>\S+)")
    rx_hostname = re.compile(r"hostname\s+(?P<hostname>\S+)", re.MULTILINE)

    def execute(self):
        fqdn=[]
#        r=self.hostname
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                   return v
            except self.snmp.TimeOutError:
                v = self.cli("show running-config configuration config")
                match = self.re_search(self.rx_hostname, v)
                if match:
                    fqdn = match.group("hostname")
                    return fqdn
                pass
 

