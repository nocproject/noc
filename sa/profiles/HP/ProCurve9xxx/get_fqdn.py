# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetFQDN
import re


##
## Get switch FQDN
## @todo: find more clean way
##
class Script(noc.sa.script.Script):
    name = "HP.ProCurve9xxx.get_fqdn"
    implements = [IGetFQDN]

    rx_hostname = re.compile(r"^hostname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain-name\s+(?P<domain>\S+)",
        re.MULTILINE)

    def execute(self):
        v = self.cli("show running-config | include ^(hostname|ip domain-name)")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return "." . join(fqdn)
