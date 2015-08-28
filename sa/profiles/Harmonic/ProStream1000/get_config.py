__author__ = 'fedoseev.ns'
# -*- coding: utf-8 -*-

##----------------------------------------------------------------------
## Harmonic.ProStream1000.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import urllib2
from lxml import etree as ET

headers = {'Content-Lenght': '640'}
data = '<AFRICA><Platform ID=\"1\" Action=\"GET_TREE\" /></AFRICA>'

import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name = "Harmonic.ProStream1000.get_config"
    implements = [IGetConfig]

    def execute(self):
        url = 'http://' + self.access_profile.address + '/BrowseConfig'
        user = self.access_profile.user
        passw = self.access_profile.password

        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, user, passw)
        auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_manager)
        urllib2.install_opener(opener)

        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        
        body = response.read()
        body = self.strip_first_lines(body, 1)
        tree = ET.XML(body)
        return ET.tostring(tree, pretty_print=True)