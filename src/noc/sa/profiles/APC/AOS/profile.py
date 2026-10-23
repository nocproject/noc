# ----------------------------------------------------------------------
# Vendor: APC
# OS:     AOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "APC.AOS"

    pattern_username = rb"^User Name\s+:"
    username_submit = b"\r"
    pattern_password = rb"^Password\s+:"
    password_submit = b"\r"
    pattern_prompt = rb"^(\S+)?>"
    pattern_more = [(rb"^Press <ENTER> to continue...$", b"\n")]
    command_submit = b"\r"

    INTERFACE_TYPES = {
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)
