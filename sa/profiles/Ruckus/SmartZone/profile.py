# ---------------------------------------------------------------------
# Vendor: Ruckus
# OS:     SmartZone
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ruckus.SmartZone"

    pattern_more = [(rb"^Login as:$", b"\n")]
    pattern_username = rb"^[Pp]lease [Ll]ogin:"
    pattern_password = rb"^[Pp]assword:"
    pattern_unprivileged_prompt = rb"^\S*>"
    pattern_prompt = rb"^\S*#"
    command_submit = b"\n"
    command_super = "enable force"
    command_leave_config = "end"
    command_exit = "exit"
