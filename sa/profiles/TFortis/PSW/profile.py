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
    username_submit = "\r\n"
    password_submit = "\r\n"
    command_submit = "\r\n"
    pattern_password = "User Password>"
    pattern_prompt = r"^TFortis .+#"
    rogue_chars = [b"\r", b"\x08*"]
    command_exit = "exit"

    def convert_interface_name(self, s):
        return s
