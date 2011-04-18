# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## cm.config_pull periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import datetime
## Django modules
from django.db.models import Q
## NOC modules
from noc.lib.periodic import Task as PeriodicTask


def reduce_config_pull(task):
    """Reduce function for cm.config_pull"""
    import datetime
    import random
    import logging
    
    from noc.settings import config
    from noc.sa.protocols.sae_pb2 import ERR_OVERLOAD, ERR_DOWN
    ## Process task results
    for mt in task.maptask_set.all():
        c = mt.managed_object.config  # Config object
        r = mt.script_result
        if mt.status == "C":
            # Completed tasks
            c.write(r)
            timeout = c.pull_every
            status = "OK"
            reason = "OK"
        elif mt.status == "F":
            # Failed tasks
            if r["code"] == ERR_OVERLOAD:
                timeout = config.getint("cm", "timeout_overload")
                status = "ERR_OVERLOAD"
            elif r["code"] == ERR_DOWN:
                timeout = config.getint("cm", "timeout_down")
                status = "ERR_DOWN"
            else:
                timeout = config.getint("cm", "timeout_error")
                status = "ERR_TIMEOUT"
            reason = r["text"]
        else:
            # Invalid state
            timeout = config.getint("cm", "timeout_error")
            status = "UNKNOWN"
            reason = "Timed out"
        # Reschedule next pull
        variation = config.getint("cm", "timeout_variation")
        # Add jitter to avoid blocking by dead task
        timeout += random.randint(-timeout / variation, timeout / variation)
        c.next_pull = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        c.save()
        logging.info("cm.config_pull: %s, status=%s, reason=%s" % (
                        mt.managed_object.name, status, reason))
    return True


class Task(PeriodicTask):
    """
    cm.config_pull periodic task
    """
    name = "cm.config_pull"
    description = ""
    default_timeout = 300
    
    def execute(self):
        # Import here to avoid circular import error
        from noc.cm.models import Config
        from noc.sa.models import ReduceTask
        # Run Map/Reduce task
        q = (Q(managed_object__is_configuration_managed=True, pull_every__isnull=False) &
            (Q(next_pull__lt=datetime.datetime.now()) | Q(next_pull__isnull=True)))
        objects = [o.managed_object for o in Config.objects.filter(q).order_by("next_pull")]
        # @todo: smarter timeout calculation
        task = ReduceTask.create_task(objects, reduce_config_pull, {},
                                      "get_config", {}, self.timeout - 3)
        return task.get_result(block=True)
    

