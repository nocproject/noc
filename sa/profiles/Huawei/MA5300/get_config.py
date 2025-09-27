# ---------------------------------------------------------------------
# Huawei.MA5300.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.MA5300.get_config"
    interface = IGetConfig
    reuse_cli_session = False

    def execute_cli(self, **kwargs):
        return self.cli("show running-config")
