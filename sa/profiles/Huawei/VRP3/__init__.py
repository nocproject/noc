# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     VRP3
# Compatible: 3.1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.VRP3"
    pattern_username = r"^>(?:\>| )User name( \(<\d+ chars\))?:"
    pattern_password = r"^>(?:\>| )(?:User )?[Pp]assword( \(<\d+ chars\))?:"
    pattern_more = [
        (r"^--More\(Enter: next line, spacebar: next page, "
            r"any other key: quit\)--", " "),
=======
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP3
## Compatible: 3.1
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH
import re


class Profile(noc.sa.profiles.Profile):
    name = "Huawei.VRP3"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^> User name \(<\d+ chars\): "
    pattern_password = r"^> Password \(<\d+ chars\): "
    pattern_more = [
        (r"^--More\(Enter: next line, spacebar: next page, any other key: quit\)--", " "),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        (r"\[<frameId/slotId>\]", "\n"),
        (r"\(y/n\) \[n\]", "y\n"),
        (r"\[to\]\:", "\n")
    ]
<<<<<<< HEAD
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?#"
    pattern_syntax_error = r"Invalid parameter|Incorrect command"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "length 0"
=======
    pattern_unpriveleged_prompt = r"^\S+?>"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager="length 0"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "save\ny\n"
<<<<<<< HEAD
=======
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?#"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
