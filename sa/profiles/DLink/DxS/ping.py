# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
from noc.sa.profiles.DLink.DxS import DGS3100
import re

class Script(NOCScript):
    name="DLink.DxS.ping"
    implements=[IPing]
    rx_result=re.compile(r"^\s*Packets: Sent =\s*(?P<count>\d+), Received =\s*(?P<success>\d+), Lost =\s*\d+",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_dgs3100=re.compile(r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss\nround-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_dgs3100_nr=re.compile(r"^\s*(?P<count>\d+) packets transmitted, 0 packets received, 100% packet loss",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    def execute(self,address,count=None,source_address=None,size=None,df=None):
        # Use one instance for perfomance
        dgs3100 = self.match_version(DGS3100)
        cmd="ping %s"%address
        if count:
            cmd+=" times %d"%int(count)
        else:
            cmd+=" times 5"
        if source_address and not dgs3100:
            cmd+=" source_ip %s"%source_address
        # Don't implemented, may be in future firmware revisions ?
        #if size:
        #    cmd+=" size %d"%int(size)
        #if df:
        #    cmd+=" df-bit"
        dgs3100_no_reply = False
        if dgs3100:
            match=self.rx_dgs3100.search(self.cli(cmd))
            if not match:
                # All packet return with "no reply"
                match=self.rx_dgs3100_nr.search(self.cli(cmd))
                dgs3100_no_reply = True
        else:
            match=self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        r = {
            "success": match.group("success") if not dgs3100_no_reply else "0",
            "count"  : match.group("count"),
        }
        if dgs3100 and not dgs3100_no_reply:
            r.update({
                "min"   : match.group("min"),
                "avg"   : match.group("avg"),
                "max"   : match.group("max"),
            })
        return r
