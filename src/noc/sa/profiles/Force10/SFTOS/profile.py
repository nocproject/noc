# ---------------------------------------------------------------------
# Vendor: Force10
# OS:     SFTOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Force10.SFTOS"

    pattern_more = [(rb"^--More-- or \(q\)uit", b"\n")]
    pattern_unprivileged_prompt = rb"^(?P<host>\S+?)>"
    pattern_prompt = rb"^(?P<host>\S+?)#"
    pattern_syntax_error = rb"% Invalid input detected at "
    pattern_operation_error = rb"% Error: "
    command_disable_pager = "terminal length 0"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory"
    command_submit = b"\r"
    convert_interface_name = BaseProfile.convert_interface_name_cisco
