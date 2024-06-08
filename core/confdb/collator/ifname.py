# ----------------------------------------------------------------------
# IfNameCollator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseCollator


class IfNameCollator(BaseCollator):
    """
    Direct map between connection name and interface name
    """

    def __init__(self, profile=None):
        super().__init__(profile=profile)
        self.names = None

    def collate(self, physical_port, interfaces):
        if not self.names:
            # Interface name
            self.names = {self.name_hash(if_name): if_name for if_name in interfaces}
            # Default name, if any
            for if_name, iface in interfaces.items():
                if iface.default_name:
                    self.names[self.name_hash(iface.default_name)] = if_name
        cn = self.name_hash(physical_port.name)
        if_name = self.names.get(cn)
        if if_name:
            return if_name
        # internal name
        if physical_port.internal_name:
            cn = self.name_hash(physical_port.name)
            return self.names.get(cn)
        return None

    @staticmethod
    def name_hash(s):
        """
        Normalized interface name hash
        :param s:
        :return:
        """
        return s.replace(" ", "").lower()
