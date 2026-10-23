# ----------------------------------------------------------------------
# Vendor: NSCComm http://www.ecitele.com/
# OS:     LPOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSCComm.LPOS"

    pattern_prompt = rb"^(?P<hostname>\S+)\s+> "
    pattern_more = [
        (rb"^\s+Press any key to continue", b"\r\n"),
        (rb"Press any letter key to start filtering items", b"\x03\r"),
    ]
    command_exit = "exit"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    pattern_syntax_error = rb"Unknown command"

    matchers = {"is_sprinter": {"platform": {"$in": ["Sprinter TX"]}}}

    @classmethod
    def get_interface_type(cls, name):
        return "physical"
