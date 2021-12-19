# ---------------------------------------------------------------------
# Vendor: Proscend
# OS:     SHDSL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Proscend.SHDSL"

    pattern_username = rb"[Uu]ser: ?"
    pattern_unprivileged_prompt = rb"^\S*>"
    command_super = "enable"
    command_exit = b"\x04"
    pattern_prompt = rb"^\S*#"
    password_submit = b"\r"

    def setup_script(self, script):
        if script.parent is None:
            password = script.credentials.get("password", "")
            if not password.endswith("\n\x15"):
                script.credentials["password"] = password + "\n\x15"
