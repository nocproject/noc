# ---------------------------------------------------------------------
# Vendor: Sun
# OS:     iLOM3
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Sun.iLOM3"

    pattern_prompt = rb"^(?:\S* )?->"
