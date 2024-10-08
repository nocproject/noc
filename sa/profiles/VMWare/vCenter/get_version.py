# ---------------------------------------------------------------------
# VMWare.vCenter.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from ..vim import VIMScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(VIMScript):
    name = "VMWare.vCenter.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self):
        v = self.vim.content.about
        return {
            "vendor": "VMWare",
            "platform": str(v.name),
            "version": v.version,
        }
