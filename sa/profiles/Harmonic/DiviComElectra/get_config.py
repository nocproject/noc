__author__ = 'FeNikS'
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Harmonic.DiviComElectra.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

#NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig
#Python modules
import re
from xml.dom.minidom import parseString

re_sub = re.compile('\n\t+\n+', re.DOTALL| re.MULTILINE)
postfix = "cgi-bin/fullxml?addLicense=yes&addFilelist=yes&addImagelist=yes&addAlarmsCurrent=yes&addAlarmsHistory=yes&addErrors=yes&"

class Script(noc.sa.script.Script):
    name = "Harmonic.DiviComElectra.get_config"
    implements = [IGetConfig]

    def execute(self):
        data = self.http.get("/" + postfix)
        parsing = parseString(data)
        data = parsing.toprettyxml()
        data = re_sub.sub('\n', data)
        return data