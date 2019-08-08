# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Iskratel
# OS:     ESCOM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.ESCOM"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Unrecognized command|% Wrong number of parameters|Incomplete command"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = [
        (r"More: <space>,  Quit: q or CTRL+Z, One line: <return>", " "),
        (r"--More--", " "),
    ]
    command_more = "a"

    matchers = {"is_escom_l": {"platform": {"$in": ["ESCOM L"]}}}
    INTERFACE_TYPES = {
        "oo": "management",
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # gigabitethernet
        "Gi": "physical",  # ESCOM L GigaEthernet
        "te": "physical",  # gigabitethernet
        "Tg": "physical",  # ESCOM L TGigaEthernet
        "Lo": "loopback",  # Loopback
        "Po": "aggregated",  # Port-channel/Portgroup
        "vl": "SVI",  # vlan
        "Vl": "SVI",  # Vlan
        "VL": "SVI",  # ESCOM L VLAM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])

    rx_escom_l = re.compile(r"(?P<type>g)(?P<number>\d+(\/\d+)+)")

    def convert_interface_name(self, interface):
        """
        >>> Profile().convert_interface_name_cisco("gi1/0/1")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name_cisco("gi1/0/1?")
        'Gi 1/0/1'
        """
        match = self.rx_escom_l.match(interface)
        if match:
            interface = "%si %s" % (match.group("type"), match.group("number"))
        return self.convert_interface_name_cisco(interface)
