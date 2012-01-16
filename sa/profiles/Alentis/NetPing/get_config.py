# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Alentis.NetPing.get_config"
    implements = [IGetConfig]

    def execute(self):
        config1 = self.http.get("/setup_get.cgi")
        config1 = config1.split("var data={")[1]
        config2 = self.http.get("/remcom_get.cgi")
        config2 = config2.split("var data={")[1]
#        config3 = self.http.get("/pwr_m_get.cgi")
#        config3 = config3.split("var data=")[1]
#        config4 = self.http.get("/pwr_get.cgi")
#        config4 = config4.split("var data=")[1]
#        config5 = self.http.get("/termo_get.cgi")
#        config5 = config5.split("var data=")[1]
        return "General Setup:\n" + config1 + \
        "\nSerial port setup:\n" + config2  # + \
        #"\nPWR setup:\n" + config3 + \
        #"\nWotchdog setup:\n" + config4 + \
        #"\nTemperature setup:\n" + config5
