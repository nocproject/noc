# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "Alentis.NetPing.get_config"
    implements = [IGetConfig]
    TIMEOUT = 300

    def execute(self):
        r = ''
        for url in ["/setup_get.cgi", "/termo_get.cgi", "/remcom_get.cgi",
            "/relay_get.cgi", "/sms_get.cgi", "/sendmail_get.cgi",
            "/io_get.cgi", "/curdet_get.cgi", "/ir_get.cgi", "/logic_get.cgi",
            "/pwr_get.cgi"]:
            conf = self.profile.var_data(self, url)
            conf = json.dumps(conf,
                sort_keys=True, indent=4, separators=(',', ': '))
            r = r + conf + '\n\n'
        return r
