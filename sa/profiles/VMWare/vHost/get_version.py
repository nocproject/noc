# ---------------------------------------------------------------------
# VMWare.vHost.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from ..vim import VIMScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(VIMScript):
    name = "VMWare.vHost.get_version"
    cache = True
    interface = IGetVersion

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        return {
            "vendor": "VMWare",
            "platform": str(h.summary.config.product.name),
            "version": h.summary.config.product.version,
        }

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.global_id)
