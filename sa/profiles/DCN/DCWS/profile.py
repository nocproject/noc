# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DCN.DCWS"
    pattern_more = [(r"^ --More-- ", "\n")]
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    command_more = "\n"
    command_submit = "\n"
    command_exit = "exit"
