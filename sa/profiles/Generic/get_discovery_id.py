# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.get_discovery_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdiscoveryid import IGetDiscoveryID


class Script(BaseScript):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Retrieve data for topology discovery
    """
    name = "Generic.get_discovery_id"
<<<<<<< HEAD
    interface = IGetDiscoveryID
=======
    implements = [IGetDiscoveryID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    requires = []

    def execute(self):
        data = {}
        with self.cached():
            x_list = (self.CLISyntaxError, self.NotSupportedError,
                      self.UnexpectedResultError)
            # Get Chassis Id
<<<<<<< HEAD
            if "get_chassis_id" in self.scripts:
=======
            if self.scripts.has_script("get_chassis_id"):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_chassis_id()
                    data["chassis_mac"] = r
            # Get fqdn
<<<<<<< HEAD
            if "get_fqdn" in self.scripts:
=======
            if self.scripts.has_script("get_fqdn"):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                with self.ignored_exceptions(x_list):
                    r = self.scripts.get_fqdn()
                    data["hostname"] = r
        return data
