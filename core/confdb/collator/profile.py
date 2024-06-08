# ----------------------------------------------------------------------
# Profile methods collator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseCollator


class ProfileCollator(BaseCollator):
    """
    Direct map between connection name and interface name
    """

    def collate(self, physical_port, interfaces) -> Optional[str]:
        for iface_name in self.profile.get_interfaces_by_port(physical_port):
            try:
                iface_name = self.profile.convert_interface_name(iface_name)
            except ValueError:
                continue
            if iface_name in interfaces:
                return interfaces[iface_name].name
