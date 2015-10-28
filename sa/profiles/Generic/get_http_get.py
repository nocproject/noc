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
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetHTTPGet


class Script(BaseScript):
    name = "Generic.get_http_get"
    interface = IGetHTTPGet
    requires = []

    def execute(self, url):
        u = urlparse.urlparse(url)
        return self.http.get(u.path, u.params or {})
