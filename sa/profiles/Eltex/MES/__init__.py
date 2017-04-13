# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Eltex
## OS:     MES
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MES"
    pattern_more = [
        (r"^More: <space>,  Quit: q, One line: <return>$", " "),
        (r"\[Yes/press any key for no\]", "Y"),
        (r"<return>, Quit: q or <ctrl>", " ")
    ]
    pattern_unpriveleged_prompt = r"^\S+> "
    pattern_syntax_error = r"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered)$"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = r"^\S+#"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        "As": "physical",  # Async
        "AT": "physical",  # ATM
        "At": "physical",  # ATM
        "BV": "aggregated",  # BVI
        "Bu": "aggregated",  # Bundle
        "C": "physical",  # @todo: fix
        "Ca": "physical",  # Cable
        "CD": "physical",  # CDMA Ix
        "Ce": "physical",  # Cellular
        "et": "physical",  # Ethernet
        "fa": "physical",  # FastEthernet
        "gi": "physical",  # GigabitEthernet
        "Gr": "physical",  # Group-Async
        "Lo": "loopback",  # Loopback
        "M": "management",  # @todo: fix
        "MF": "aggregated",  # Multilink Frame Relay
        "Mf": "aggregated",  # Multilink Frame Relay
        "Mu": "aggregated",  # Multilink-group interface
        # "PO": "physical",    # Packet OC-3 Port Adapter
        "Po ": "aggregated",  # Port-channel/Portgroup
        "Po": "aggregated",  # Port-channel/Portgroup
        "R": "aggregated",  # @todo: fix
        "SR": "physical",  # Spatial Reuse Protocol
        "Se": "physical",  # Serial
        "te": "physical",  # TenGigabitEthernet
        "Tu": "tunnel",  # Tunnel
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
        "vl": "SVI",  # vlan Eltex ver 1.1.38
        "XT": "SVI"  # Extended Tag ATM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
