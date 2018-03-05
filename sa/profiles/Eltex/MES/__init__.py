# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MES
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MES"
    pattern_more = [
        (r"^More: <space>,  Quit: q, One line: <return>$", " "),
        (r"\[Yes/press any key for no\]", "Y"),
        (r"<return>, Quit: q or <ctrl>", " "),
        (r"q or <ctrl>+z", " "),
        (r"Overwrite file \[startup-config\].... \(Y\/N\)", "Y"),
        (r"Would you like to continue \? \(Y\/N\)\[N\]", "Y")
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>\s*"
    pattern_syntax_error = \
        r"^% (Unrecognized command|Incomplete command|" \
        r"Wrong number of parameters or invalid range, size or " \
        r"characters entered)$"
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = \
        r"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\,\(\)\/]+)?" \
        r"(?:\(config[^\)]*\))?#"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        "as": "physical",    # Async
        "at": "physical",    # ATM
        "bv": "aggregated",  # BVI
        "bu": "aggregated",  # Bundle
        # "C": "physical",     # @todo: fix
        "ca": "physical",    # Cable
        "cd": "physical",    # CDMA Ix
        "ce": "physical",    # Cellular
        "et": "physical",    # Ethernet
        "fa": "physical",    # FastEthernet
        "gi": "physical",    # GigabitEthernet
        "gr": "physical",    # Group-Async
        "lo": "loopback",    # Loopback
        # "M": "management",   # @todo: fix
        "mf": "aggregated",  # Multilink Frame Relay
        "mu": "aggregated",  # Multilink-group interface
        "po": "aggregated",  # Port-channel/Portgroup
        # "R": "aggregated",   # @todo: fix
        "sr": "physical",    # Spatial Reuse Protocol
        "se": "physical",    # Serial
        "te": "physical",    # TenGigabitEthernet
        "fo": "physical",    # FortyGigabitEthernet
        "tu": "tunnel",      # Tunnel
        "vl": "SVI",         # VLAN, found on C3500XL
        "xt": "SVI"          # Extended Tag ATM
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
