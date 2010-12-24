# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
##
## EdgeCore.ES.get_version
##
class Script(NOCScript):
    name="EdgeCore.ES.get_version"
    cache=True
    implements=[IGetVersion]
    ##
    ## Main dispatcher
    ##
    def execute(self):
        try:
            v=self.cli("show system")
        except self.CLISyntaxError:
            # Get 4xxx version
            return self.get_version_4xxx()
        return self.get_version_35xx(v)
    ##
    ## 35xx
    ##
    rx_sys_35=re.compile(r"^\s*System description\s*:\s(?P<platform>.+?)\s*$",re.MULTILINE|re.IGNORECASE)
    rx_ver_35=re.compile(r"^\s*Operation code version\s*:\s*(?P<version>\S+)\s*$",re.MULTILINE|re.IGNORECASE)
    def get_version_35xx(self, show_system):
        # Detect version
        v=self.cli("show version")
        match=self.re_search(self.rx_ver_35, v)
        version=match.group("version")
        # Detect platform
        match=self.re_search(self.rx_sys_35, show_system)
        platform=match.group("platform")
        if "ES3526XA" in platform:
            # Detect ES3626XA hardware version
            sub=version.split(".")
            if sub[0]=="1":
                platform="ES3526XA-V2"
            elif sub[0]=="2" and sub[1]=="3":
                if int(sub[2])&1==1:
                    platform="ES3526XA-38"
                else:
                    platform="ES3526XA-1-SL-38"
            else:
                raise self.NotSupportedError(platform)
        elif "3510MA" in platform:
            platform="ES3510MA"
        elif "3510" in platform:
            platform="ES3510"
        elif "3552M" in platform:
            platform="ES3552M"
        elif "3528" in platform or "ES3526S" in platform:
            pass
        elif platform.lower()=="8 sfp ports + 4 gigabit combo ports l2/l3/l4 managed standalone switch":
            platform="ES4612"
        else:
            raise self.NotSupportedError(platform)
        return {
            "vendor"    : "EdgeCore",
            "platform"  : platform,
            "version"   : version,
        }
    
    ##
    ## ES4626
    ##
    rx_sys_4=re.compile(r"BootRom Version\s+.*?(?P<platform>ES.+?)_",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_ver_4=re.compile(r"SoftWare (Package )?Version.*?_(?P<version>\d.+?)$",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    def get_version_4xxx(self):
        v=self.cli("show version 1")
        match_sys=self.re_search(self.rx_sys_4, v)
        match_ver=self.re_search(self.rx_ver_4, v)
        return {
            "vendor"    : "EdgeCore",
            "platform"  : match_sys.group("platform"),
            "version"   : match_ver.group("version"),
        }
    
