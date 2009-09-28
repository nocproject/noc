# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco ASA Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,DROP_EVENT,CLOSE_EVENT
from noc.fm.rules.classes.config import *
from noc.fm.rules.classes.default import DROP

##
## Cisco.ASA Config Changed SYSLOG
##
class Cisco_ASA_Config_Changed_SYSLOG_Rule(ClassificationRule):
    name="Cisco.ASA Config Changed SYSLOG"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.ASA$"),
        (r"^message$",r"^%ASA-5-111004: \S+ end configuration: OK$"),
        (r"^source$",r"^syslog$"),
    ]
