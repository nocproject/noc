# ---------------------------------------------------------------------
# Vendor: HP
# OS:     GbE2c
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.GbE2"

    pattern_more = [(rb"Press q to quit, any other key to continue", b" ")]
    pattern_prompt = rb"^>> [^#]+# "
    command_leave_config = "apply"
    command_save_config = "save\ny\n"
    config_volatile = [r"^/\* Configuration dump taken.*?$"]
    rogue_chars = [b"\x08"]
