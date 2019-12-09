# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Intracom
# OS:     UltraLink
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Intracom.UltraLink"
    pattern_prompt = r"^(?P<hostname>\S+)>"
    command_exit = "exit"
    pattern_syntax_error = r"Syntax Error: Invalid Command"
    command_save_config = "config save"

    def cleaned_config(self, config):
        config = config.replace("--\n", "")
        config = super(Profile, self).cleaned_config(config)
        return config
