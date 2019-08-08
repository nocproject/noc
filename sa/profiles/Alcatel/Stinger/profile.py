# -*- coding: utf-8 -*-
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
    pattern_prompt = r"^\S+>"
    pattern_username = "User: "
    pattern_password = "Password: "
    command_exit = "quit"
