# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration Changes events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## Equipment configuraion changed
##
class ConfigChanged(EventClass):
    name     = "Config Changed"
    category = "NETWORK"
    priority = "INFO"
    subject_template="Configuration changed"
    body_template="""Equipment configuration changed"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger="on_config_changed"
    class Vars:
        user=Var(required=False)
##
## Config Synced
##
class ConfigSynced(EventClass):
    name     = "Config Synced"
    category = "SYSTEM"
    priority = "INFO"
    subject_template="Config has been synced"
    body_template="""Config has been synced"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
