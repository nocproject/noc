# ---------------------------------------------------------------------
# VMWare.vHost.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from ..vim import VIMScript


class Script(VIMScript):
    name = "VMWare.vHost.get_capabilities"

    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        h = self.vim.get_host_by_id(self.controller.global_id)
        return bool(h.capabilities.supportsNetworkHints)
