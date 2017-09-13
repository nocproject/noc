# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Linksys
# HW:     SWR
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    # @todo supercli mode (Ctrl+Z lcli)
    name = "Linksys.SWR"
    pattern_prompt = r"(ArrowKey/TAB/BACK=Move  SPACE=Toggle  ENTER=Select  ESC=Back)|^>"
    command_super = "lcli"
    # pattern_unpriveleged_prompt = "^>"
    pattern_username = "User Name:"
    username_submit = "\t"
    pattern_password = "Password:"
    password_submit = "\r\n"
    command_submit = "\r\n"
    enable_cli_session = False
    command_exit = "\x1Alogout"
    rogue_chars = [re.compile(r"\x1b\[\d+;0H\x1b\[K"), re.compile(r"\x1b\[\d;2[47]"), "\r"]
