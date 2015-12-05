# -*- coding: utf-8 -*-
__author__ = 'FeNikS'

##----------------------------------------------------------------------
## SUMAVISION.EMR.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import urllib2
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_ver = re.compile(r"VID_WEB_VER = \"(?P<ver>.*?)\"", re.DOTALL|re.MULTILINE)


class Script(BaseScript):
    name = "Sumavision.EMR.get_version"
    interface = IGetVersion

    def execute(self):
        version = ''
        try:
            url = ''.join(['http://', self.access_profile.address, '/en/version_info.asp'])
            user = self.access_profile.user
            passw = self.access_profile.password

            password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(None, url, user, passw)
            auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
            opener = urllib2.build_opener(auth_manager)
            urllib2.install_opener(opener)

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            body = response.read()
            version = rx_ver.search(body).group("ver")
        except Exception:
            pass

        return {
            "vendor": "Sumavision",
            "platform": "EMR",
            "version": version if version else "Unknown"
        }
