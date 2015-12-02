# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MapTask Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.core.service.client import RPCClient


logger = logging.getLogger(__name__)


class MTManagerImplementation(object):
    def __init__(self, limit=0):
        self.limit = limit

    def run(self, object, script, params=None, timeout=None):
        """
        Run SA script and wait for result
        """
        if "." in script:
            # Leave only script name
            script = script.split(".")[-1]
        return RPCClient("sae", calling_service="MTManager").script(
            object.id, script, params, timeout
        )


# Run single instance
MTManager = MTManagerImplementation()
