# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raritan.DominionSX.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os

# Third-party modules
from six.moves.urllib.parse import urlparse

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Raritan.DominionSX.get_config"
    interface = IGetConfig

    def execute(self, **kwargs):
        self.cli("maintenance")
        with self.servers.ftp() as ftp:
            p = urlparse(ftp.get_url(self.access_profile.address))
            path, file = os.path.split(p.path)
            self.cli(
                "backup ip %s login anonymous password anonymous path %s file %s"
                % (p.netloc, path, file)
            )
            config = ftp.get_data()
        self.cli("top")
        return self.cleaned_config(config)
