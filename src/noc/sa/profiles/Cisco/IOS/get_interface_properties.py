# ----------------------------------------------------------------------
# Cisco.IOS.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript


class Script(BaseScript):
    name = "Cisco.IOS.get_interface_properties"

    def interface_filter(self, interface):
        """
        Check interface by name, False is ignored
        :param interface: Interface name
        :return:
        """
        try:
            self.profile.convert_interface_name(interface)
        except ValueError:
            return False
        return True
