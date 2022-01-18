# ---------------------------------------------------------------------
# Vendor: CData
# OS:     xPON
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "CData.xPON"
    pattern_more = r"  --More \( Press 'Q' to quit \)--"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>(?!#)\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    pattern_syntax_error = r"Unknown command: \("
    command_more = " "
    # command_disable_pager = "vty output show-all"
    command_super = "enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "save"
    command_exit = "exit"
    config_volatile = ["^%.*?$"]
