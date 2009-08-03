# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS specific logging rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.logging import *
##
## Cisco.IOS Logged Command SYSLOG
##
class Cisco_IOS_Logged_Command_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Logged Command SYSLOG"
    event_class=LoggedCommand
    preference=1000
    action=CLOSE_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%PARSER-5-CFGLOG_LOGGEDCMD: User:(?P<user>\S+)  logged command:(?P<command>.*)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS Logging Started SYSLOG
##
class Cisco_IOS_Logging_Started_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Logging Started SYSLOG"
    event_class=LoggingStarted
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%SYS-6-LOGGINGHOST_STARTSTOP: Logging to host (?P<host>\S+) port (?P<port>\d+) started"),
        (r"^profile$",r"^Cisco\.IOS$"),
    ]
