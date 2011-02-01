# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS FreeBSD Chassis-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.chassis import *
##
## OS.FreeBSD Cold Start SYSLOG
##
class OS_FreeBSD_Cold_Start_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD Cold Start SYSLOG"
    event_class=SystemColdStart
    preference=1000
    patterns=[
        (r"^message$",r"kernel: FreeBSD is a registered trademark of The FreeBSD Foundation."),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]
