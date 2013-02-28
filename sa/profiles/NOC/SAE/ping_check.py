# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.ping_check
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import Queue
import datetime
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPingCheck
from noc.sa.protocols.sae_pb2 import *


class Script(NOCScript):
    name = "NOC.SAE.ping_check"
    implements = [IPingCheck]

    def execute(self, activator_name, addresses):
        def callback(transaction, response=None, error=None):
            if error:
                queue.put([])
            else:
                queue.put([
                    {"ip": r.address, "status": r.status}
                    for r in response.status
                ])

        try:
            stream = self.sae.get_activator_stream(
                activator_name, can_ping=True)
        except Exception, why:
            self.error("Ping error: %s" % why)
            return []
        r = PingCheckRequest()
        for a in addresses:
            r.addresses.append(a)
        stream.proxy.ping_check(r, callback)
        # Use queue to receive result from callback
        queue = Queue.Queue()
        return queue.get()
