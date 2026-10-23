# ---------------------------------------------------------------------
# VMWare.vHost.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from ..vim import VIMScript


class Script(BaseScript, VIMScript):
    name = "VMWare.vHost.get_capabilities"

    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        h = self.vim.get_host_by_id(self.controller.global_id)
        if not bool(h.config.capabilities.supportsNetworkHints):
            return False
        hints = h.configManager.networkSystem.QueryNetworkHint()
        return hints and hints[0].lldpInfo

    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        h = self.vim.get_host_by_id(self.controller.global_id)
        if not bool(h.config.capabilities.supportsNetworkHints):
            return False
        hints = h.configManager.networkSystem.QueryNetworkHint()
        return hints and hints[0].connectedSwitchPort
