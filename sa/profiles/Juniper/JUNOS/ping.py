# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS..ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Juniper.JUNOS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, (\d+\.)?\d+% packet loss\nround-trip min/avg/max/stddev "
        r"= (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)/\d+\.\d+ ms",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, (\d+\.)?\d+% packet loss\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, vrf=None
    ):
        cmd = "ping no-resolve"
        if count:
            cmd += " count %d" % int(count)
        else:
            cmd += " count 5"
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            cmd += " do-not-fragment"
        if vrf:
            cmd += " routing-instance %s" % vrf
        cmd += " %s" % address
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
            }
        else:
            match = self.rx_result1.search(s)
            return {
                "success": match.group("success"),
                "count": match.group("count")
            }
