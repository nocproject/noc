__author__ = "FeNikS"
# ---------------------------------------------------------------------
# Harmonic.DiviComElectra.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

# Python modules
import re
from xml.dom.minidom import parseString


class Script(BaseScript):
    name = "Harmonic.DiviComElectra.get_config"
    interface = IGetConfig

    postfix = "cgi-bin/fullxml?addLicense=yes&addFilelist=yes&addImagelist=yes&addAlarmsCurrent=yes&addAlarmsHistory=yes&addErrors=yes&"
    rx_sub = re.compile("\n\t+\n+", re.DOTALL | re.MULTILINE)

    def execute(self):
        data = self.http.get("/" + self.postfix)
        parsing = parseString(data)
        data = parsing.toprettyxml()
        return self.rx_sub.sub("\n", data)
