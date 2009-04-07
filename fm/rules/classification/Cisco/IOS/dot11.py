# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS 802.11 classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression
from noc.fm.rules.classes.dot11 import *

##
## CISCO.IOS dot11 Associated
##
class CISCO_IOS_dot11_Associated_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Associated SNMP"
    event_class=Dot11Associated
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-6-ASSOC:.+?(?P<raw_mac>\S+) (?:A|Rea)ssociated"),
        (r"^profile$",r"^Cisco\.IOS$"),
        Expression("mac","decode_mac(raw_mac)")
    ]
##
## Cisco.IOS dot11 Disassociated
##
class Cisco_IOS_dot11_Disassociated_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Disassociated SNMP"
    event_class=Dot11Disassociated
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-6-DISASSOC: .+?(?P<raw_mac>\S+) Reason"),
        (r"^profile$",r"^Cisco\.IOS$"),
        Expression("mac","decode_mac(raw_mac)")
    ]
##
## Cisco.IOS dot11 Max Retries SYSLOG
##
class Cisco_IOS_dot11_Max_Retries_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Max Retries SYSLOG"
    event_class=Dot11MaxRetries
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-4-MAXRETRIES: Packet to client (?P<raw_mac>\S+) reached max retries, removing the client$"),
        Expression("mac","decode_mac(raw_mac)")
    ]
##
## Cisco.IOS dot11 Max Retries SYSLOG SNMP
##
class Cisco_IOS_dot11_Max_Retries_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Max Retries SYSLOG SNMP"
    event_class=Dot11MaxRetries
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.",r"^Packet to client (?P<raw_mac>\S+) reached max retries, removing the client$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.",r"^DOT11$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.",r"^MAXRETRIES$"),
        Expression("mac","decode_mac(raw_mac)")
    ]
