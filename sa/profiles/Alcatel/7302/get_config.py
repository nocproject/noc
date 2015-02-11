# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name = "Alcatel.7302.get_config"
    implements = [IGetConfig]

    noc.sa.script.telnet.CLITelnetSocket.TTL = 600

    def execute(self):
        self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:30")
        config = self.cli("info configure flat")
        return self.cleaned_config(config)
