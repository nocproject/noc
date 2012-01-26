# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: MikroTik
## OS:     RouterOS
## Compatible: 3.14 and above
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "MikroTik.RouterOS"
    supported_schemes = [TELNET, SSH]
    command_submit = "\r"
    pattern_prompt = r"\[(?P<prompt>.+?@.+?)\] > "
    pattern_more = [
        ("Please press \"Enter\" to continue!", "\n"),
    ]
    pattern_syntax_error = r"bad command name"
    config_volatile = [r"^#.*?$", r"^\s?"]

    # Starting from v3.14 we can specify console options during login process.
    def setup_script(self, script):
        if script.parent is None \
        and not script.access_profile.user.endswith("+ct"):
            script.access_profile.user += "+ct"
