# ---------------------------------------------------------------------
# Vendor: Raritan
# OS:     DominionSX
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raritan.DominionSX"

    pattern_prompt = rb"^(\S+ > )+"
    pattern_more = [(rb"--More-- Press <ENTER> to continue.", b"\r")]
