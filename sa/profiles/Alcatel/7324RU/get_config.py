# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.7324RU.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.7324RU.get_config"
    interface = IGetConfig

    def execute(self):
        try:
            response = self.http.get("/config-0_20200101_0101.dat")
        except self.http.HTTPError:
            return self.cleaned_config("")
        # @todo: Auth
        return self.cleaned_config(response.body)
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
