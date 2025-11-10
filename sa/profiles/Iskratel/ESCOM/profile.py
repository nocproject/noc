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

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = (
        rb"% Unrecognized command|% Wrong number of parameters|Incomplete command"
    )
    command_super = b"enable"
    command_disable_pager = "terminal datadump"
    pattern_more = [
        (rb"More: <space>,  Quit: q or CTRL+Z, One line: <return>", b" "),
        (rb"--More--", b" "),
    ]

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
        "p": "Port-aggregator",  # ESCOM L Port-channel/Portgroup
        "vl": "SVI",  # vlan
        "Vl": "SVI",  # Vlan
        "VL": "SVI",  # ESCOM L VLAM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])

    rx_escom_l = re.compile(r"(?P<type>g|p)(?P<number>\d+(\/\d+)+)")

    def convert_interface_name(self, interface):
        """
        >>> Profile().convert_interface_name("gi1/0/1")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name("gi1/0/1?")
        'Gi 1/0/1'
        >>> Profile().convert_interface_name("p1")
        'Port-aggregator 1'
        """
        match = self.rx_escom_l.match(interface)
        if interface.startswith("p"):
            # ESCOM L Port-channel/Portgroup
            return f"Port-aggregator {interface[1:]}"
        if match:
            interface = "%si %s" % (match.group("type"), match.group("number"))
        return self.convert_interface_name_cisco(interface.strip("?"))
