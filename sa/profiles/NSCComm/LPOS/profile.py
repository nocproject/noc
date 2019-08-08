# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: NSCComm http://www.ecitele.com/
# OS:     LPOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSCComm.LPOS"
    pattern_prompt = r"^(?P<hostname>\S+)\s+> "
    pattern_more = [
        (r"^\s+Press any key to continue", "\r\n"),
        (r"Press any letter key to start filtering items", "\x03\r"),
    ]
    command_exit = "exit"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
