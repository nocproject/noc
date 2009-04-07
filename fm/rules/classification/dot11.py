# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS IPsec classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression
from noc.fm.rules.classes.dot11 import *
##
## Dot11 Deauthenticate SNMP
##
class Dot11_Deauthenticate_SNMP_Rule(ClassificationRule):
    name="Dot11 Deauthenticate SNMP"
    event_class=Dot11Deauthenticate
    preference=1000
    required_mibs=["IEEE802dot11-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.2\.840\.10036\.1\.6\.0\.2$"),
        (r"^1\.2\.840\.10036\.1\.1\.1\.18\.1$",r"(?P<bin_mac>......)"),
        Expression("mac","decode_mac(bin_mac)"),
    ]
