# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DxS
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="DLink.DxS"
    supported_schemes=[TELNET,SSH]
    pattern_username="([Uu]ser ?[Nn]ame|[Ll]ogin):"
    pattern_password="[Pp]ass[Ww]ord:"
    pattern_more="CTRL\+C.+?a All"
    pattern_unpriveleged_prompt=r"^\S+:(3|6|user|operator)#"
    pattern_syntax_error=r"(Available commands|Next possible completions|Ambiguous token):"
    command_super="enable admin"
    pattern_prompt=r"^(?P<hostname>\S+(:\S+)*)#"
    command_disable_pager="disable clipaging"
    command_more="a"
    command_exit="logout"
    command_save_config="save"
    config_volatile=["^%.*?$"]
    ##
    ## Version comparison
    ## Version format:
    ## <major>.<minor><sep><patch>
    ##
    rx_ver=re.compile(r"\d+")
    def cmp_version(self, x, y):
        return cmp([int(z) for z in self.rx_ver.findall(x)], [int(z) for z in self.rx_ver.findall(y)])

    cluster_member = None
    dlink_pager = False
    rx_pager=re.compile(r"^(Clipaging|CLI Paging)\s+:\s*(?P<cp>Enabled|Disabled)\s*$", re.MULTILINE)
    def setup_session(self, script):
        # Cache "show switch" command and fetch CLI Paging from it
        match = self.rx_pager.search(script.cli("show switch", cached=True))
        if match:
            self.dlink_pager = (match.group("cp") == "Enabled")

        # Parse path parameters
        for p in script.access_profile.path.split("/"):
            if p.startswith("cluster:"):
                self.cluster_member=p[8:].strip()
        # Switch to cluster member, if necessary
        if self.cluster_member:
            script.debug("Switching to SIM member '%s'"%script.cluster_member)
            script.cli("reconfig member_id %s"%script.cluster_member)

    def shutdown_session(self, script):
        if self.cluster_member:
            script.cli("reconfig exit")
        if self.dlink_pager:
            script.cli("enable clipaging")
        else:
            script.cli("disable clipaging")

## DES-3200-series
def DES3200(v):
    return v["platform"].startswith("DES-3200")

## DGS-3120-series
def DGS3120(v):
    return v["platform"].startswith("DGS-3120")

## DGS-3400-series
def DGS3400(v):
    return "DGS-3420" not in v["platform"] and v["platform"].startswith("DGS-34")

## DGS-3420-series
def DGS3420(v):
    return v["platform"].startswith("DGS-3420")


## DGS-3600-series
def DGS3600(v):
    return "DGS-3610" not in v["platform"] and "DGS-3620" not in v["platform"] and v["platform"].startswith("DGS-36")

## DGS-3620-series
def DGS3620(v):
    return v["platform"].startswith("DGS-3620")
