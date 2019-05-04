# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7324RU.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
from noc.core.script.http.base import HTTPError


class Script(BaseScript):
    name = "Alcatel.7324RU.get_config"
    interface = IGetConfig

    def execute(self, **kwargs):
        try:
            response = self.http.get("/config-0_20200101_0101.dat")
        except HTTPError:
            return self.cleaned_config("")
        # @todo: Auth
        return self.cleaned_config(response.body)
