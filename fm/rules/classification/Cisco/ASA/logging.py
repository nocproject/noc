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
## Cisco.ASA Logged Command SYSLOG
##
class Cisco_ASA_Logged_Command_SYSLOG_Rule(ClassificationRule):
    name="Cisco.ASA Logged Command SYSLOG"
    event_class=LoggedCommand
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.ASA$"),
        (r"^collector$",r"^192\.168\.155\.11:514$"),
        (r"^message$",r"^%ASA-5-111008: User '(?P<user>\S+)' executed the '(?P<command>.*)' command\.$"),
        (r"^source$",r"^syslog$"),
    ]
