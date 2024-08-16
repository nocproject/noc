# ---------------------------------------------------------------------
# VMWare.vHost.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
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
        return self.execute_controller(hid=self.controller.local_id)
