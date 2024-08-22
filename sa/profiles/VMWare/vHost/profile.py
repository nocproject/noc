# ---------------------------------------------------------------------
# Vendor: VMWare
# OS:     vHost
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "VMWare.vHost"

    def convert_interface_name(self, s):
        return s
