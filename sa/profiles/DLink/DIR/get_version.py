# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DIR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DLink.DIR.get_version"
    interface = IGetVersion
    cache = True

    def execute(self, **kwargs):
        baseURL = "/cliget.cgi?cmd="
        r = {"vendor": "DLink",
             "platform": "DIR Undefined",
             "version": ""}

        param = {"platform": "$sys_model",
                 "hw_ver": "$hw_cver",
                 "version": "$sw_ver"}
        # /cliget.cgi?cmd=$sys_model%;echo"%;$hw_cver%;echo"%;$sw_ver%;echo"
        req = "%;".join(["%;".join((param[p], "echo\"")) for p in param])

        urlpath = baseURL + req + ";"
        self.logger.debug("URL path is: %s" % urlpath)

        rr = self.http.get(urlpath)
        rr = rr.splitlines()

        self.logger.debug("Result: %s " % rr)
        if rr:
            r = {"vendor": "DLink",
                 "platform": rr[0],
                 "version": rr[2],
                 "attributes": {
                    "HW version": rr[1],
                 }
                 }
        return r
