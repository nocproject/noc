# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT8500
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT8500"

    pattern_more = [
        (rb"^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit", b"c")
    ]
    command_submit = b"\r"
    command_save_config = "save configuration"
    pattern_prompt = rb"^\S+?#"
