# ----------------------------------------------------------------------
# Juniper.JUNOS.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript


class Script(BaseScript):
    name = "Juniper.JUNOS.get_interface_properties"

    def interface_filter(self, interface):
        return self.profile.valid_interface_name(self, interface)
