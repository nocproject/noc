# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.VoIP.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
from noc.lib.text import strip_html_tags


class Script(noc.sa.script.Script):
    name = "Linksys.VoIP.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac = re.compile(r"^MAC Address:+(?P<mac>\S+)+Client Certificate:",
                        re.MULTILINE)

    def execute(self):
        mac = self.http.get("/")
        mac = strip_html_tags(mac)
        mac = self.rx_mac.search(mac)
        return mac.group("mac")
