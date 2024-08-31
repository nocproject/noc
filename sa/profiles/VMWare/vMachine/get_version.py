# ---------------------------------------------------------------------
# VMWare.vMachine.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from ..vim import VIMScript
from noc.sa.interfaces.igetversion import IGetVersion


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
        return self.execute_controller(hid=self.controller.local_id)