# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Linksys.VoIP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.lib.text import strip_html_tags


class Script(BaseScript):
    name = "Linksys.VoIP.get_chassis_id"
    cache = True
    interface = IGetChassisID
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_mac = re.compile(r"^MAC Address:+(?P<mac>\S+)+Client Certificate:",
                        re.MULTILINE)

    def execute(self):
        mac = self.http.get("/")
        mac = strip_html_tags(mac)
        mac = self.rx_mac.search(mac)
        mac = mac.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
