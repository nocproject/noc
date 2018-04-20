# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Ericsson
# OS:     SEOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ericsson.SEOS"
    pattern_more = "^---(more)---"
    pattern_unprivileged_prompt = \
        r"^(?:\[(?P<context>\S+)\])?(?P<hostname>\S+)>"
    pattern_prompt = r"^(?:\[(?P<context>\S+)\])?(?P<hostname>\S+)#"
=======
##----------------------------------------------------------------------
## Vendor: Ericsson
## OS:     SEOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Ericsson.SEOS"
    supported_schemes = [TELNET, SSH]
    pattern_more = "^---(more)---"
    pattern_unpriveleged_prompt = r"^\S+?>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"% Invalid input at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
<<<<<<< HEAD
=======
    pattern_prompt = r"^\[(?P<context>\S+)\](?P<hostname>\S+)#"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
