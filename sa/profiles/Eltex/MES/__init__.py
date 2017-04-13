# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Eltex
## OS:     MES
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
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
               "as": "physical",    # Async
               "at": "physical",    # ATM
               "bv": "aggregated",  # BVI
               "bu": "aggregated",  # Bundle
               #"C": "physical",     # @todo: fix
               "ca": "physical",    # Cable
               "cd": "physical",    # CDMA Ix
               "ce": "physical",    # Cellular
               "et": "physical",    # Ethernet
               "fa": "physical",    # FastEthernet
               "gi": "physical",    # GigabitEthernet
               "gr": "physical",    # Group-Async
               "lo": "loopback",    # Loopback
               #"M": "management",   # @todo: fix
               "mf": "aggregated",  # Multilink Frame Relay
               "mu": "aggregated",  # Multilink-group interface
               "po": "aggregated",  # Port-channel/Portgroup
               #"R": "aggregated",   # @todo: fix
               "sr": "physical",    # Spatial Reuse Protocol
               "se": "physical",    # Serial
               "te": "physical",    # TenGigabitEthernet
               "tu": "tunnel",      # Tunnel
               "vl": "SVI",         # VLAN, found on C3500XL
               "xt": "SVI"          # Extended Tag ATM
               }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())                                    