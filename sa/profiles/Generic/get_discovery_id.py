# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_discovery_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdiscoveryid import IGetDiscoveryID


class Script(BaseScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_discovery_id"
    interface = IGetDiscoveryID
    requires = []

    def execute(self):
        data = {}
        with self.cached():
            x_list = (self.CLISyntaxError, self.NotSupportedError,
                      self.UnexpectedResultError)
            # Get Chassis Id
            if "get_chassis_id" in self.scripts:
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_chassis_id()
                    data["chassis_mac"] = r
            # Get fqdn
            if "get_fqdn" in self.scripts:
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_fqdn()
                    data["hostname"] = r
        return data
