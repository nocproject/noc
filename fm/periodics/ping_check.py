# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Runs PING probe of all hosts
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import math
import random
import time
## NOC modules
import noc.lib.periodic


def reduce_ping(task, periodic):
    """Reduce script for ping_check"""
    r = False
    for mt in task.maptask_set.all():
        if mt.status == "C":
            r = True
        else:
            periodic.error("Ping failed on activator '%s': %s" % (
                mt.script_params["activator_name"], mt.script_result
            ))
    return r


class Task(noc.lib.periodic.Task):
    name = "fm.ping_check"
    description = ""
    default_timeout = 50

    def execute(self):
        from noc.sa.models import Activator, ReduceTask

        objects = {}  # activator -> [objects]
        # Look for addresses
        for a in Activator.objects.filter(is_active=True):
            o = [o.trap_source_ip for o in
                 a.managedobject_set.filter(trap_source_ip__isnull=False,
                                            is_managed=True)]
            if o:
                objects[a.name] = o
        if not objects:
            return True
        # Detect number of task and size of chunk
        I = 10
        t = (self.timeout - 5) / I
        # Schedule
        for a in objects:
            o = objects[a]
            s = int(math.ceil(float(len(o)) / I))
            x = [o[s * i:s * (i + 1)] for i in range(I)]
            random.shuffle(x)
            objects[a] = x
        tasks = []
        # Run tasks every t seconds
        for i in range(I):
            # Prepare task parameters
            for a in objects:
                o = objects[a].pop(0)
                if o:
                    tasks += [ReduceTask.create_task(
                        "SAE",
                        reduce_ping, {"periodic": self},
                        "ping_check", {"activator_name": a, "addresses": o},
                         t * 2)]
            time.sleep(t)
        # Collect task results
        r = True
        for task in tasks:
            r &= task.get_result(block=True)
        return r
