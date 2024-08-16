# ---------------------------------------------------------------------
# VMWare.vHost.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "VMWare.vHost.get_fqdn"
    cache = True
    interface = IGetFQDN

    def execute_controller(self, hid: str):
        h = self.vim.get_host_by_id(hid)
        return h.summary.config.name

    def execute(self, **kwargs):
        return self.execute_controller(hid=self.controller.local_id)
