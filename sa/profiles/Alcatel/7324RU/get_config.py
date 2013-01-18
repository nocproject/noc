# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7324RU.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.protocols.sae_pb2 import HTTP
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "Alcatel.7324RU.get_config"
    implements = [IGetConfig]

    def execute(self):
        self.access_profile.scheme == self.HTTP
        config = self.http.get("/config-0_20200101_0101.dat")
        return self.cleaned_config(config)
