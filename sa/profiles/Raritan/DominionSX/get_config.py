# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Raritan.DominionSX.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
import urlparse
import os

class Script(BaseScript):
    name = "Raritan.DominionSX.get_config"
    interface = IGetConfig
=======
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
import urlparse
import os

class Script(noc.sa.script.Script):
    name = "Raritan.DominionSX.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        self.cli("maintenance")
        with self.servers.ftp() as ftp:
            p = urlparse.urlparse(ftp.get_url(self.access_profile.address))
            path, file = os.path.split(p.path)
            self.cli("backup ip %s login anonymous password anonymous path %s file %s" % (p.netloc, path, file))
            config = ftp.get_data()
        self.cli("top")
        return self.cleaned_config(config)
