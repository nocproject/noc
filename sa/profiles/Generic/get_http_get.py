# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_http_get
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import urlparse
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetHTTPGet


class Script(NOCScript):
    name = "Generic.get_http_get"
    implements = [IGetHTTPGet]
    requires = []

    def execute(self, url):
        u = urlparse.urlparse(url)
        return self.http.get(u.path, u.params or {})
