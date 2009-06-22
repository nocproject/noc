# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DES3xxx Link-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.link import *
##
## DLink.DES35xx Link Down SYSLOG
##
class DLink_DES35xx_Link_Down_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES35xx Link Down SYSLOG"
    event_class=LinkDown
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
        (r"^message$",r"INFO: Port (?P<interface>\S+) link down"),
    ]

##
## DLink.DES35xx Link Up SYSLOG
##
class DLink_DES35xx_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES35xx Link Up SYSLOG"
    event_class=LinkUp
    preference=1000
    patterns=[
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"INFO: Port (?P<interface>\S+) link up"),
    ]
