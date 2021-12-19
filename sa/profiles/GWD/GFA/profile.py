# ---------------------------------------------------------------------
# Vendor: GWD (GW Delight Technology Co., Ltd) http://www.gwdelight.com
# OS:     GFA
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "GWD.GFA"

    pattern_more = [(rb"Press any key to continue", b" ")]
    pattern_syntax_error = rb"% Unknown command.|% Command incomplete."
    pattern_unprivileged_prompt = rb"^\S+?>"
    pattern_prompt = rb"^\S+\(config\)?#"
    command_super = "enable"
    command_disable_pager = "screen lines 0"

    def convert_interface_name(self, interface):
        if interface.startswith("eth") or interface.startswith("pon"):
            interface = interface[3:]
        return interface
