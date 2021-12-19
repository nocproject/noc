# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     AireOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.AireOS"

    pattern_username = rb"^User:"
    pattern_more = [(rb"--More-- or \(q\)uit", b"\n")]
    pattern_prompt = rb"^\(Cisco Controller\)\s+>"
    requires_netmask_conversion = True
