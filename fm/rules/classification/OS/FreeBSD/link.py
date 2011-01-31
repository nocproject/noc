# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS FreeBSD Link-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.link import *
##
## OS.FreeBSD Link Down SYSLOG
##
class OS_FreeBSD_Link_Down_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD Link Down SYSLOG"
    event_class=LinkDown
    preference=1000
    patterns=[
        (r"^message$",r"(?P<interface>\S+): link state changed to DOWN"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]

##
## OS.FreeBSD Link Up SYSLOG
##
class OS_FreeBSD_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD Link Up SYSLOG"
    event_class=LinkUp
    preference=1000
    patterns=[
        (r"^message$",r"(?P<interface>\S+): link state changed to UP"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]
