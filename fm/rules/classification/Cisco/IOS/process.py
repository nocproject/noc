# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS specific process rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.process import *
##
## Cisco.IOS Process Traceback SYSLOG
##
class Cisco_IOS_Process_Traceback_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Process Traceback SYSLOG"
    event_class=ProcessTraceback
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"Process= \"(?P<process>[^\"]+)\", .*, pid= (?P<pid>\d+),  -Traceback="),
    ]