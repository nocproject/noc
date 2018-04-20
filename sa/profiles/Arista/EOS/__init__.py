# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Arista
# OS:     EOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile
from noc.sa.interfaces.base import InterfaceTypeError


class Profile(BaseProfile):
    name = "Arista.EOS"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Invalid input"
=======
##----------------------------------------------------------------------
## Vendor: Arista
## OS:     EOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.interfaces import InterfaceTypeError


class Profile(NOCProfile):
    name = "Arista.EOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = r"% Invalid input"
    pattern_username = "Login:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"\?\s*\[confirm\]", "\n")
    ]
    command_submit = "\r"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
<<<<<<< HEAD
    convert_mac = BaseProfile.convert_mac_to_cisco
=======
    convert_mac = NOCProfile.convert_mac_to_cisco
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_interface_name = re.compile("^(?P<type>\S+?)(?P<number>\d+)$")

    def convert_interface_name(self, s):
        match = self.rx_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
<<<<<<< HEAD
        return "%s%s" % (match.group("type")[:2], match.group("number"))
=======
        return "%s%s" % (match.group("type")[:2], match.group("number"))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
