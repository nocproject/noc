# ---------------------------------------------------------------------
# VMWare.vMachine.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.error import ERR_CLI_AUTH_FAILED, NOCError
from noc.sa.interfaces.igetversion import IGetVersion

from ..vim import VIMScript


class Script(VIMScript):
    name = "VMWare.vMachine.get_version"
    cache = True
    interface = IGetVersion

    def execute_controller(self, hid: str):
        vm = self.vim.get_vm_by_id(hid)
        return {
            "vendor": "VMWare",
            "platform": str(vm.config.guestId),
            "version": vm.config.guestFullName,
        }

    def execute(self, **kwargs):
        if not self.controller:
            raise NOCError(code=ERR_CLI_AUTH_FAILED, msg="Not set Controller")
        return self.execute_controller(hid=self.controller.global_id)
