# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raritan.DominionSX.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IGetConfig
import urlparse,os

class Script(noc.sa.script.Script):
    name="Raritan.DominionSX.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("maintenance")
        with self.servers.ftp() as ftp:
            p=urlparse.urlparse(ftp.get_url(self.access_profile.address))
            path,file=os.path.split(p.path)
            self.cli("backup ip %s login anonymous password anonymous path %s file %s"%(p.netloc,path,file))
            config=ftp.get_data()
        self.cli("top")
        return self.cleaned_config(config)
