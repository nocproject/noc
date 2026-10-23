# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     FWSM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.FWSM"

    pattern_more = [(rb"^<--- More --->", b" ")]
    pattern_unprivileged_prompt = rb"^\S+?>"
    command_super = b"enable"
    pattern_prompt = rb"^\S+?#"
