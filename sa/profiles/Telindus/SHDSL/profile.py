# ---------------------------------------------------------------------
# Vendor: Telindus
# OS:     SHDSL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Telindus.SHDSL"

    username_submit = b"\r"
    password_submit = b"\r"
    command_exit = "DISCONNECT"
