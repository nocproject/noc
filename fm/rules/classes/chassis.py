# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Chassis-related events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass, Var
##
## System Cold Start
##
class SystemColdStart(EventClass):
    name     = "Cold Start" 
    category = "NETWORK" 
    priority = "NORMAL" 
    subject_template="System cold start" 
    body_template="""System cold start""" 
    repeat_suppression=False
    repeat_suppression_interval=3600

##
## Fan Failed
##
class FanFailed(EventClass):
    name     = "Fan Failed" 
    category = "NETWORK" 
    priority = "MAJOR" 
    subject_template="Fan Failed" 
    body_template="""Fan RPM value is lower than its limit RPM value""" 
    repeat_suppression=True
    repeat_suppression_interval=3600

##
## Fan Recovered
##
class FanRecovered(EventClass):
    name     = "Fan Recovered" 
    category = "NETWORK" 
    priority = "NORMAL" 
    subject_template="Fan Recovered" 
    body_template="""The RPM of the fan has recovered to normal state""" 
    repeat_suppression=True
    repeat_suppression_interval=3600
