# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression
from noc.fm.rules.classes.auth import *
##
## Authentication Failure SNMP
## Provides IP address
##
class Authentication_Failure_SNMP_Rule(ClassificationRule):
    name="Authentication Failure SNMP"
    event_class=AuthenticationFailure
    preference=1000
    required_mibs=["SNMPv2-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.5$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.2\.1\.5\.0$",r"(?P<bin_ip>....)"),
        Expression("ip","decode_ipv4(bin_ip)"),
    ]
##
## Authentication Failure Simple SNMP
## Matches when no IP address provided
##
class Authentication_Failure_Fallback_SNMP_Rule(ClassificationRule):
    name="Authentication Failure Fallback SNMP"
    event_class=AuthenticationFailure
    preference=2000
    required_mibs=["SNMPv2-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.5$"), # authenticationFailure
    ]
