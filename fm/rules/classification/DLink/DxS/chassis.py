# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DxS Chassis-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.chassis import *

##
## DLink.DxS Cold Start  SYSLOG
##
class DLink_DxS_Cold_Start_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Cold Start SYSLOG"
    event_class=SystemColdStart
    preference=1000
    patterns=[
        (r"^message$",r"System cold start"),
        (r"^source$", r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
##
## DLink.DxS Fan Failed SYSLOG
##
class DLink_DxS_Fan_Failed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Fan Failed SYSLOG"
    event_class=FanFailed
    preference=1000
    patterns=[
        (r"^message$",r"Fan \d+ failed"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
##
## DLink.DxS Fan Recovered SYSLOG
##
class DLink_DxS_Fan_Recovered_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Fan Recovered SYSLOG" 
    event_class=FanRecovered
    preference=1000
    patterns=[
        (r"^message$",r"Fan \d+ recovered"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
