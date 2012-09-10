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

## Python modules
import datetime
## NOC modules
from noc.inv.discovery.scheduler import DiscoveryScheduler

CONFIG_DELAY = 10  # Minutes to delay config fetch
INTERFACE_DELAY = 15  # Minutes to delay interface fetch

discovery_scheduler = DiscoveryScheduler()

@pyrule
def refresh_config(event):
    now = datetime.datetime.now()
    # Check managed object is managed
    if not event.managed_object.is_managed:
        return
    # Schedule config fetch
    next_pull = event.timestamp + datetime.timedelta(minutes=CONFIG_DELAY)
    if next_pull < datetime.datetime.now():  # next_pull points to the past
        return
    try:
        config = event.managed_object.config
        config.next_pull = next_pull
        config.save()
    except Exception:
        return  # No config found
    # Schedule interface fetch
    discovery_scheduler.reschedule_job(
        job_name="interface_discovery",
        key=event.managed_object.id,
        ts=now + datetime.timedelta(minutes=INTERFACE_DELAY)
    )
