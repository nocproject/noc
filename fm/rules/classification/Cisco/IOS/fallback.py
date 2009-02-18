# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS fallback rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.fallback import *
##
## Cisco.IOS Unhandled SNMP Syslog
##
class Cisco_IOS_Unhandled_SNMP_Syslog_Rule(ClassificationRule):
    name="Cisco.IOS Unhandled SNMP Syslog"
    event_class=UnhandledSyslog
    preference=90000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"), # clogMessageGenerated
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"(?P<message>.*)"),        # clogHistMsgText
    ]
