# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.discovery.scheduler import get_scheduler

DELAY = 600
discovery_scheduler = get_scheduler()


def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
    # Check managed object is managed
    if not event.managed_object.is_managed:
        return
    event.managed_object.run_discovery(DELAY)
