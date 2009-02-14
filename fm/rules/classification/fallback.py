# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fallback classification rules
## Fallback classes are based on event source type only (SNMP Trap, Syslog)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.fallback import *
##
## Match any unhandled SNMP Trap
##
class UnhandledSNMPRule(ClassificationRule):
    name="Unhandled SNMP"
    event_class=UnhandledSNMPTrap
    preference=100000
    patterns=[
        (r"^source$",                          r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$", r"(?P<oid>\S+)"), # snmpTrapOID.0
    ]
##
## Match any unhandled Syslog message
##
class UnhandledSyslogRule(ClassificationRule):
    name="Unhandled Syslog"
    event_class=UnhandledSyslog
    preference=100000
    patterns=[
        (r"^source$",   r"^syslog$"),
    ]
