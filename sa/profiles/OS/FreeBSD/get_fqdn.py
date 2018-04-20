# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# OS.FreeBSD.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^(?P<hostname>\S+)")

    def execute(self):
        match = self.rx_hostname.search(self.cli("hostname"))
        return match.group("hostname")
=======
##----------------------------------------------------------------------
## OS.FreeBSD.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_fqdn"
    implements = [IGetFQDN]
    rx_hostname = re.compile(r"^(?P<hostname>\S+)")

    def execute(self):
        fqdn = []
        match = self.rx_hostname.search(self.cli("hostname"))
        if match:
            fqdn += [match.group("hostname")]
        return fqdn
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
