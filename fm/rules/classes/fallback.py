# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fallback event classes description
## Fallback classes are based on event source type only (SNMP Trap, Syslog)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## Fallback for all unprocessed SNMP traps
##
class UnhandledSNMPTrap(EventClass):
    name="SNMP Trap"
    subject_template="trap: {{oid}}"
    body_template="""Unhandled SNMP trap:
----------
{{oid}}
----------"""
    class Vars:
        oid=Var(required=True)

##
## Fallback for all unprocessed Syslog messages
##
class UnhandledSyslog(EventClass):
    name="SYSLOG"
    subject_template="syslog: {{message}}"
    body_template="""Unhandled syslog message:
----------
{{message}}
----------"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    class Vars:
        message=Var(required=True,repeat=True)
