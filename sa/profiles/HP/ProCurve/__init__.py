# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: HP
# OS:     ProCurve
# ---------------------------------------------------------------------
# Copyright (C) 2007-10 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.ProCurve"
    pattern_prompt = r"^[a-zA-Z0-9- _/.]+?(\(\S+\))?# "
    pattern_unprivileged_prompt = r"^[a-zA-Z0-9- _/.]+?> "
    pattern_more = [
        ("Press any key to continue", "\n"),
        ("-- MORE --, next page: Space, next line: Enter, quit: Control-C", " ")
    ]
=======
##----------------------------------------------------------------------
## Vendor: HP
## OS:     ProCurve
##----------------------------------------------------------------------
## Copyright (C) 2007-10 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "HP.ProCurve"
    supported_schemes = [TELNET, SSH]
    pattern_prompt = r"^[a-zA-Z0-9- _]+?(\(\S+\))?# "
    pattern_unpriveleged_prompt = r"^[a-zA-Z0-9- _]+?> "
    pattern_more = [
        ("Press any key to continue", "\n"),
        ("-- MORE --, next page: Space, next line: Enter, quit: Control-C", " ")
        ]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"Invalid input: "
    command_disable_pager = "terminal length 1000"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_exit = "exit"

<<<<<<< HEAD
    #
    # Compare versions
    #
    # Version format is <letter>.<major>.<minor>
    #
=======
    ##
    ## Compare versions
    ##
    ## Version format is <letter>.<major>.<minor>
    ##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @classmethod
    def cmp_version(cls, v1, v2):
        l1, mj1, mn1 = v1.split(".")
        l2, mj2, mn2 = v2.split(".")
        if l1 != l2:
            # Different letters
            return None
        r = cmp(int(mj1), int(mj2))
        if r != 0:
            return r
        return cmp(int(mn1), int(mn2))
