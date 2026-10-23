# ---------------------------------------------------------------------
# Vendor: Cambium
# OS:     ePMP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cambium.ePMP"
    # pattern_username = "([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
    # pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = rb"^(?P<hostname>\S+)>"
    # config_volatile = ["^%.*?$"]

    @classmethod
    def get_interface_type(cls, name):
        return "physical"
