# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: FreeBSD
# OS:     FreeBSD
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.FreeBSD"
    command_super = "su"
    command_exit = "exit"
    pattern_username = r"^[Ll]ogin:"
    pattern_unprivileged_prompt = r"^\S*?\s*(%|\$)\s*"
=======
##----------------------------------------------------------------------
## Vendor: FreeBSD
## OS:     FreeBSD
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "OS.FreeBSD"
    supported_schemes = [TELNET, SSH]
    command_super = "su"
    command_exit = "exit"
    pattern_username = r"^[Ll]ogin:"
    pattern_unpriveleged_prompt = r"^\S*?\s*(%|\$)\s*"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^(?P<hostname>\S*)\s*#\s*"
    pattern_syntax_error = r": Command not found\."
