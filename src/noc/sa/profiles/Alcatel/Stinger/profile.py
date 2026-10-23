# ----------------------------------------------------------------------
# Vendor: Alcatel
# HW:     Stinger
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.Stinger"

    pattern_prompt = rb"^\S+>"
    pattern_username = rb"User: "
    pattern_password = rb"Password: "
    command_exit = "quit"
