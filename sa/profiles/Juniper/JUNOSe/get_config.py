# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    """
    Junos.JUNOSe.get_config
    """
    name = "Juniper.JUNOSe.get_config"
    implements = [IGetConfig]
    rx_service = re.compile("^(?P<service>\w+\.mac)", re.MULTILINE)

    def execute(self):
        # Get configuration
        try:
            config = self.cli("show running-configuration")
        except self.CLISyntaxError:
            config = self.cli("show configuration")
        configs = [{
                "name": "config",
                "config": self.cleaned_config(config)
            }]
        # Get services
        self.cli("terminal width 200")
        r = self.cli("show service-management service-definition brief | include True")
        for s in self.rx_service.findall(r):
            configs += [{
                "name": "service %s" % s,
                "config": self.cleaned_config(self.cli("more %s" % s))
            }]
        return configs
