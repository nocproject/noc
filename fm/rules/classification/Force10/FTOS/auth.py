# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication-related events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classes.auth import *
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
##
## Force10.FTOS Authentication Failure SNMP
##
class Force10_FTOS_Authentication_Failure_SNMP_Rule(ClassificationRule):
    name="Force10.FTOS Authentication Failure SNMP"
    event_class=AuthenticationFailure
    preference=1000
    required_mibs=["F10-CHASSIS-MIB"]
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.5$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.6027\.3\.1\.1\.4\.1\.2$",r"^SNMP_AUTH_FAIL: SNMP Authentication failure for SNMP request from host (?P<ip>\S+)$"),
    ]
