# ---------------------------------------------------------------------
# Vendor: HP
# OS:     iLO2
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.iLO2"

    pattern_username = rb"Login Name:"
    pattern_prompt = rb"hpiLO->"
    command_submit = b"\r"
