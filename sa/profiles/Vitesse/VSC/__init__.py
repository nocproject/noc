# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Vitesse (Vitesse Semiconductor)
# OS:     VSC
# URL: http://www.microsemi.com/products/ethernet-solutions/ethernet-switches
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Vitesse.VSC"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Invalid word detected at"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    command_submit = "\r"
    username_submit = "\r"
    password_submit = "\r"
    pattern_more = "-- more --, next page: Space, continue: g, quit: ^"
    command_more = "g"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Gi 1/3")
        'GigabitEthernet 1/3'
        >>> Profile().convert_interface_name("2.5G 1/2")
        '2.5GigabitEthernet 1/2'
        >>> Profile().convert_interface_name("10G 1/1")
        '10GigabitEthernet 1/1'
        """
        s = s.strip()
        if s.startswith("Gi "):
            return "GigabitEthernet %s" % s[3:].strip()
        if s.startswith("2.5G "):
            return "2.5GigabitEthernet %s" % s[5:].strip()
        if s.startswith("10G G "):
            return "10GigabitEthernet %s" % s[4:].strip()
        return s
