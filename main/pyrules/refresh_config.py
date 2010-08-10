# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Refresh config
##----------------------------------------------------------------------
## INTERFACE: IEvent
##----------------------------------------------------------------------
## DESCRIPTION:
## Reschedule device configuration to fetch
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import datetime

DELAY=10 # Minutes to delay config fetch

@pyrule
def refresh_config(event):
    next_pull=event.timestamp+datetime.timedelta(minutes=DELAY)
    if next_pull<datetime.datetime.now(): # next_pull points to the past
        return
    try:
        config=event.managed_object.config
    except:
        return # No config found
    config.next_pull=next_pull
    config.save()

