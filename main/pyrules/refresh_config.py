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
from noc.inv.models import DiscoveryStatusInterface

CONFIG_DELAY = 10  # Minutes to delay config fetch
INTERFACE_DELAY = 15  # Minutes to delay interface fetch


@pyrule
def refresh_config(event):
    # Check managed object is managed
    if not event.managed_object.is_managed:
        return
    # Schedule config fetch
    next_pull = event.timestamp + datetime.timedelta(minutes=CONFIG_DELAY)
    if next_pull < datetime.datetime.now():  # next_pull points to the past
        return
    try:
        config = event.managed_object.config
    except:
        return  # No config found
    config.next_pull = next_pull
    config.save()
    # Schedule interface fetch
    DiscoveryStatusInterface.reschedule(event.managed_object,
                                        INTERFACE_DELAY * 60)
