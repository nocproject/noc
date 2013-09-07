# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_discovery_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDiscoveryID


class Script(NOCScript):
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_discovery_id"
    implements = [IGetDiscoveryID]
    requires = []

    def execute(self):
        data = {}
        with self.cached():
            x_list = (self.CLISyntaxError, self.NotSupportedError,
                      self.UnexpectedResultError)
            # Get Chassis Id
            if self.scripts.has_script("get_chassis_id"):
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_chassis_id()
                    data["chassis_mac"] = r
            # Get fqdn
            if self.scripts.has_script("get_fqdn"):
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_fqdn()
                    data["hostname"] = r
        return data
