# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.ping_check
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import Queue
import datetime
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IPingCheck
from noc.sa.protocols.sae_pb2 import *


class Script(noc.sa.script.Script):
    name = "NOC.SAE.ping_check"
    implements = [IPingCheck]

    def execute(self, activator_name, addresses):
        def callback(transaction, response=None, error=None):
            def save_probe_result(u, result, ts):
                # @todo: Make ManagedObject's method
                mo = ManagedObject.objects.filter(activator=activator,
                                            trap_source_ip=u).order_by("id")
                if len(mo) < 1:
                    self.error("Unknown object: %s" % u)
                    return
                # Fetch first-created object in case of multiple objects
                # with same trap_source_ip
                mo = mo[0]
                # Update object status
                self.sae.object_status[mo.id] = (result == "success")
                # Save event to database
                self.sae.write_event(
                    data=[("source", "system"),
                          ("activator", activator_name),
                          ("probe", "ping"),
                          ("ip", u),
                          ("result", result)],
                    managed_object=mo,
                    timestamp=ts)

            if error:
                queue.put([])
            else:
                ts = datetime.datetime.now()
                for u in response.unreachable:
                    save_probe_result(u, "failed", ts)
                for u in response.reachable:
                    save_probe_result(u, "success", ts)
                queue.put(([{"ip": ip, "status": True}
                            for ip in response.reachable] +
                           [{"ip": ip, "status": False}
                            for ip in response.unreachable]))

        try:
            stream = self.sae.get_activator_stream(activator_name)
        except Exception, why:
            return []
        from noc.sa.models import ManagedObject, Activator
        activator = Activator.objects.get(name=activator_name)
        r = PingCheckRequest()
        for a in addresses:
            r.addresses.append(a)
        stream.proxy.ping_check(r, callback)
        # Use queue to receive result from callback
        queue = Queue.Queue()
        return queue.get()
