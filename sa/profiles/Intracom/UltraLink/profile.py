# ---------------------------------------------------------------------
# Vendor: Intracom
# OS:     UltraLink
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Intracom.UltraLink"

    pattern_prompt = rb"^(?P<hostname>\S+)>"
    command_exit = "exit"
    pattern_syntax_error = rb"Syntax Error: Invalid Command"
    command_save_config = "config save"

    def cleaned_config(self, config):
        config = config.replace("--\n", "")
        return super().cleaned_config(config)
