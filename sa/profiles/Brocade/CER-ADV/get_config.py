# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.CER-ADV.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Brocade.CER-ADV.get_config
    """
    name = 'Brocade.CER-ADV.get_config'
<<<<<<< HEAD
    interface = IGetConfig
=======
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        config = self.cli('show config')
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
