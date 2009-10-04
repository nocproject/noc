# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sun.iLOM3.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Sun.iLOM3.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("cd /SP/config")
        with self.servers.ftp() as ftp:
            url=ftp.get_url(self.access_profile.address)
            self.cli("dump -destination %s"%url)
            config=ftp.get_data()
        self.cli("cd /")
        return self.cleaned_config(config)
