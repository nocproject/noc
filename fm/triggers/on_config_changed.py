# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## on_config_changed
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.fm.triggers
import datetime
##
## on_config_changed trigger sets next_pull of next config check to
## event time +10 minutes. If resulting next_pull points to past
## next pull will left unaltered
##
class EventTrigger(noc.fm.triggers.EventTrigger):
    name="on_config_changed"
    def handle(self,event):
        next_pull=event.timestamp+datetime.timedelta(minutes=10)
        if next_pull<datetime.datetime.now(): # next_pull points to the past
            return
        try:
            config=event.managed_object.config
        except:
            return # No config found
        config.next_pull=next_pull
        config.save()
