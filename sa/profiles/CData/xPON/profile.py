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
    pattern_more = [(rb"  --More \( Press 'Q' to quit \)--", b" ")]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>"
    pattern_prompt = rb"^(?P<hostname>(?!#)\S+?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    pattern_syntax_error = rb"Unknown command: \("
    # command_disable_pager = "vty output show-all"
    command_super = b"enable"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_save_config = "save"
    command_exit = "exit"
    config_volatile = ["^%.*?$"]
