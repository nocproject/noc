__author__ = 'FeNikS'
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Harmonic.bNSG9000.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urllib2
from xml.dom.minidom import parseString
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name = "Harmonic.bNSG9000.get_config"
    implements = [IGetConfig]

    data = '<PYTHON><Platform ID=\"1\" Action=\"GET_TREE\" /></PYTHON>'
    rx_sub = re.compile('\n\t+\n+', re.MULTILINE| re.DOTALL)

    def execute(self):
        url = 'http://' + self.access_profile.address + '/BrowseConfig'
        user = self.access_profile.user
        passw = self.access_profile.password

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, user, passw)
        auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_manager)
        urllib2.install_opener(opener)

        req = urllib2.Request(url, self.data)
        response = urllib2.urlopen(req)

        config = response.read()
        config = self.strip_first_lines(config, 1)
        config = parseString(config)
        config = config.toprettyxml()
        config = self.rx_sub.sub('\n', config)
        config = config.replace(">\n</", "></")

        return config