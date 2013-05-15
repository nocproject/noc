# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Refresh config
##----------------------------------------------------------------------
## INTERFACE: IEventTrigger
##----------------------------------------------------------------------
## DESCRIPTION:
## Reschedule device configuration to fetch
## Used in event trigger for Config | Config Changed event class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.discovery.scheduler import DiscoveryScheduler

DELAY = 600

discovery_scheduler = DiscoveryScheduler()

@pyrule
def refresh_config(event):
    # Check managed object is managed
    if not event.managed_object.is_managed:
        return
    event.managed_object.run_discovery(DELAY)
