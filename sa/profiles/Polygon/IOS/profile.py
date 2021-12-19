# ---------------------------------------------------------------------
# Vendor: Polygon
# OS:     IOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Polygon.IOS"

    pattern_more = [(rb"^ --More--", " "), (r"(?:\?|interfaces)\s*\[confirm\]", b" ")]
    pattern_unpriveleged_prompt = rb"^\S+?>"
    pattern_syntax_error = (
        rb"% Invalid input detected at|% Ambiguous command:|% Incomplete command."
    )
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "copy running-config startup-config\n"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?(?:\(config[^\)]*\))?#"
    requires_netmask_conversion = True
    convert_mac = BaseProfile.convert_mac_to_cisco
    config_volatile = ["^ntp clock-period .*?^"]
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
