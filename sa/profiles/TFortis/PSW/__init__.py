# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: TFortis
# OS:     PSW
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "TFortis.PSW"
    pattern_username = "User Name>"
    pattern_password = "User Password>"
    pattern_prompt = r"^TFortis .+#"
    command_exit = "exit"

    def convert_interface_name(self, s):
        return s
