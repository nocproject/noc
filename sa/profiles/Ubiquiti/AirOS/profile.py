# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Ubiquiti
# OS:     AirOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ubiquiti.AirOS"
    pattern_username = r"([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
    pattern_more = r"CTRL\+C.+?a All"
    pattern_prompt = r"^\S+?\.v(?P<version>\S+)#"
    command_more = "a"
    config_volatile = [r"^%.*?$"]
