# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS DNS-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.dns import *
##
## Cisco.IOS Bad DNS Query SYSLOG
##
class Cisco_IOS_Bad_DNS_Query_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Bad DNS Query SYSLOG"
    event_class=BadDNSQuery
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%DNSSERVER-3-BADQUERY: Bad DNS query from (?P<ip>\S+)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS Bad DNS Query SYSLOG SNMP
##
class Cisco_IOS_Bad_DNS_Query_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Bad DNS Query SYSLOG SNMP"
    event_class=BadDNSQuery
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^BADQUERY$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^Bad DNS query from (?P<ip>\S+)$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^DNSSERVER$"),
    ]
