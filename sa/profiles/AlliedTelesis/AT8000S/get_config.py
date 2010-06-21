# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
#from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.get_config"
    implements=[IGetConfig]
    def execute(self):
        # this version is buggy because of hardcoded 
        # line wraps in output of "show running-config"
        self.cli("terminal datadump")
        config=self.cli("show running-config")
        # new variant with tftp file copy
        # waiting for bugfixes in NOC's tftp server
        #        with self.servers.tftp() as tftp:
        #            url=tftp.get_url(self.access_profile.address)
        #            self.cli("copy running-config %s"%url)
        #            config=tftp.get_data()
        return self.cleaned_config(config)
