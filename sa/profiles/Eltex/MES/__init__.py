# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Vendor: Eltex
## OS:     MES
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(NOCProfile):
    name = "Eltex.MES"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^User Name:"
    pattern_password = r"^Password:"
    pattern_more = [
        (r"^More: <space>,  Quit: q, One line: <return>$", " "),
        (r"\[Yes/press any key for no\]", "Y")
        ]
    pattern_unpriveleged_prompt = r"^\S+> "
    pattern_syntax_error = r"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered)$"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
<<<<<<< HEAD
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
=======
    pattern_prompt = r"^\S+#"
    convert_interface_name = NOCProfile.convert_interface_name_cisco
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
