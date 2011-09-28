# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Juniper
## OS:     JUNOSe
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(NOCProfile):
    """
    Juniper.JUNOSe profile
    """
    name = "Juniper.JUNOSe"
    supported_schemes = [TELNET, SSH]
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    pattern_prompt = r"^(?P<prompt>\S+?)(?::\S+?)?#"
    pattern_more = r"^ --More-- "
    command_more = " "
    pattern_syntax_error = r"% Invalid input detected at"
    config_volatile = [r"^! Configuration script being generated on.*?^",
                       r"^(Please wait\.\.\.)\n",
                       r"^(\.+)\n"]
    rogue_chars = ["\r", "\x00", "\x0d"]

    ##
    ## Common forms are:
    ##    X.Y.Z release-A.B
    ##    X.Y.Z patch-A.B
    @classmethod
    def cmp_version(self, v1, v2):
        def convert(v):
            return v.replace(" patch-", ".").replace(" release-", ".")
        return NOCProfile.cmp_version(convert(v1), convert(v2))
