# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Linksys.VoIP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.lib.text import strip_html_tags


class Script(BaseScript):
    name = "Linksys.VoIP.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Linksys.VoIP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetVersion
from noc.lib.text import strip_html_tags


class Script(noc.sa.script.Script):
    name = "Linksys.VoIP.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_platform = re.compile(
        r"^Product Name:+(?P<platform>\S+)+Serial Number:+(?P<serial>\S+)$",
        re.MULTILINE)
    rx_version = re.compile(
<<<<<<< HEAD
        r"^Software Version:+(?P<version>\S+)+Hardware Version:+"
        r"(?P<hardware>\S+)$",
=======
        r"^Software Version:+(?P<version>\S+)+Hardware Version:+(?P<hardware>\S+)$",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        re.MULTILINE)

    def execute(self):
        v = self.http.get("/")
        v = strip_html_tags(v)
        platform = self.rx_platform.search(v)
        version = self.rx_version.search(v)
        return {
                "vendor": "Linksys",
                "platform": platform.group("platform"),
                "version": version.group("version"),
                "attributes": {
                            "HW version": version.group("hardware"),
<<<<<<< HEAD
                            "Serial Number": platform.group("serial")
=======
                            "Serial Number": platform.group("serial"),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            }
                }
