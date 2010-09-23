# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.ping_check
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IPingCheck
from noc.sa.protocols.sae_pb2 import *
import Queue

class Script(noc.sa.script.Script):
    name="NOC.SAE.ping_check"
    implements=[IPingCheck]
    def execute(self,activator_name,addresses):
        def callback(transaction,response=None,error=None):
            if error:
                queue.put([])
            else:
                queue.put([{"ip":ip,"status":True} for ip in response.reachable]+[{"ip":ip,"status":False} for ip in response.unreachable])
        stream=self.sae.get_activator_stream(activator_name)
        r=PingCheckRequest()
        for a in addresses:
            r.addresses.append(a)
        stream.proxy.ping_check(r,callback)
        # Use queue to receive result from callback
        queue=Queue.Queue()
        return queue.get()
