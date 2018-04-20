# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Vyatta
# OS:     Vyatta
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Vyatta.Vyatta"
=======
##----------------------------------------------------------------------
## Vendor: Vyatta
## OS:     Vyatta
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Vyatta.Vyatta"
    supported_schemes = [TELNET, SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_username = r"[Ll]ogin: (?!\S+)"
    pattern_prompt = r"^(?P<username>\S+)@(?P<hostname>\S+):[^$]+\$ "
    pattern_more = [
        (r"^:", " "),
        (r"\[confirm\]", "\n")
    ]
<<<<<<< HEAD
    command_disable_pager = "set terminal length 0"
=======
    command_disable_pager = "terminal length 0"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_enter_config = "configure"
    command_leave_config = "commit\nexit"

    @classmethod
    def get_interface_type(cls, name):
        if name.startswith("eth"):
            return "physical"
        elif name.startswith("lo"):
            return "loopback"
        elif name.startswith("br"):
            return "aggregated"
        elif name.startswith("vtun"):
            return "tunnel"
        else:
            raise Exception("Cannot detect interface type for %s" % name)
