# ----------------------------------------------------------------------
# VCENTER Port mapper
# ----------------------------------------------------------------------
# Copyright (C) 2022-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.etl.portmapper.base import BasePortMapper


class VCENTERPortMapper(BasePortMapper):
    #
    # default
    #
    def to_remote(self, name, iface_hints=None):
        """
        Convert interface name
        """
        return name

    def to_local(self, name, iface_hints=None):
        return name
