# -*- coding: utf-8 -*-
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
    """
    Brocade.CER-ADV.get_config
    """
    name = 'Brocade.CER-ADV.get_config'
    implements = [IGetConfig]

    def execute(self):
        config = self.cli('show config')
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
