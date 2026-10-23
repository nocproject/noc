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

    @classmethod
    def allow_allow_asymmetric_link(cls, method: str):
        return method == "lacp"

    def convert_interface_name(self, s):
        return s

    def get_lacp_port_by_id(self, port_id: int):
        """
        Return possible port aliases by LACP Port id,
        i.e. for LACP discovery method without script support
        Can be overriden to achieve desired behavior
        """
        return f"vmnic{int(port_id) - 1}"
