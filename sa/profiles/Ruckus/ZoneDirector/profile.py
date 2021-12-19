# ---------------------------------------------------------------------
# Vendor: Ruckus
# OS:     ZoneDirector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ruckus.ZoneDirector"

    pattern_more = [(rb"^Login as:$", b"\n")]
    pattern_username = b"^[Pp]lease [Ll]ogin:"
    pattern_password = b"^[Pp]assword:"
    pattern_unprivileged_prompt = rb"^\S*>"
    pattern_prompt = rb"^\S*#"
    command_submit = b"\n"
    command_super = "enable force"
    command_leave_config = "end"
    command_exit = "exit"
