# ----------------------------------------------------------------------
# Vendor: Linksys
# HW:     SWR
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    # @todo supercli mode (Ctrl+Z lcli)
    name = "Linksys.SRW"

    pattern_prompt = rb"(ArrowKey/TAB/BACK=Move  SPACE=Toggle  ENTER=Select  ESC=Back)|^>"
    command_super = b"lcli"
    # pattern_unprivileged_prompt = "^>"
    pattern_username = rb"User Name:"
    username_submit = b"\t"
    pattern_password = rb"Password:"
    password_submit = b"\r\n"
    command_submit = b"\r\n"
    enable_cli_session = False
    command_exit = "\x1alogout"
    rogue_chars = [re.compile(rb"\x1b\[\d+;0H\x1b\[K"), re.compile(rb"\x1b\[\d;2[47]"), b"\r"]
