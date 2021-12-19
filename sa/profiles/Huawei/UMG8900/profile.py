# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     UMG8900 media gateway
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.UMG8900"

    pattern_username = b"Login :"
    pattern_password = b"Password :"
    pattern_more = rb"^Press CTRL\+C to break, other key to continue\.\.\."
    pattern_prompt = rb"mml>"
    command_more = " "
    rogue_chars = [b"\r"]
    config_volatile = [r"^\+\+\+.*?$"]
