# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig

class Script(BaseScript):
    name="Audiocodes.Mediant2000.get_config"
    interface = IGetConfig
    def execute(self):
        if self.access_profile.scheme in [self.TELNET,self.SSH]:
            self.cli("conf")
            config=self.cli("cf get")
        elif self.access_profile.scheme==self.HTTP:
            config=self.http.get("/FS/BOARD.ini")
        else:
            raise Exception("Unsupported access scheme")
        return self.cleaned_config(config)
