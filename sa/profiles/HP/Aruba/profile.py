# ---------------------------------------------------------------------
# Vendor: HP
# OS:     Aruba
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Aruba"

    INTERFACE_TYPES = {6: "physical", 53: "SVI"}
