# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vitesse.VSC.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.lib.validators import is_ipv4, is_ipv6
import re


class Script(BaseScript):
    name = "Vitesse.VSC.ping"
    interface = IPing
    rx_result = re.compile(
        r"Sent (?P<count>\d+) packets, received (?P<success>\d+) OK, \d+ bad")

    def execute(self, address, count=None, source_address=None, size=None,
    df=None, vrf=None):
        if is_ipv4(address):
            cmd = "ping ip %s" % address
        elif is_ipv6(address):
            cmd = "ping ipv6 %s" % address
        if count:
            cmd += " repeat %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        return match.groupdict()
