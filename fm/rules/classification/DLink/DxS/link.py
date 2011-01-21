# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DxS Link-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.link import *
##
## DLink.DxS Link Down SYSLOG
##
class DLink_DxS_Link_Down_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Link Down SYSLOG"
    event_class=LinkDown
    preference=1000
    patterns=[
        (r"^message$",r"Port (?P<interface>\S+) link down"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]

##
## DLink.DxS Link Up SYSLOG
##
class DLink_DxS_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Link Up SYSLOG"
    event_class=LinkUp
    preference=1000
    patterns=[
        (r"^message$",r"Port (?P<interface>\S+) link up"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
