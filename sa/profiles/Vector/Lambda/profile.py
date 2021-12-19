# ----------------------------------------------------------------------
# Vendor: Vector
# OS:     Lambda
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.snmp.render import render_mac


class Profile(BaseProfile):
    name = "Vector.Lambda"

    pattern_username = rb"^ login: "
    pattern_password = rb"^ password: "
    pattern_prompt = rb"^>"
    command_exit = "logout"
    pattern_syntax_error = rb"invalid command: .*"

    matchers = {
        "is_sysid_support": {"caps": {"$in": ["SNMP | OID | EnterpriseID"]}},
        "is_vectrar2d2": {"platform": {"$in": ["VectraR2D2 Nano"]}},
    }

    snmp_display_hints = {
        "1.3.6.1.4.1.5591.1.3.2.7.0": render_mac,
        "1.3.6.1.4.1.34652.2.11.5.1.0": render_mac,
        "1.3.6.1.4.1.17409.1.3.2.1.1.1.0": render_mac,
    }
