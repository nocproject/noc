# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS 802.11 classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.radius import *
##
## Cisco.IOS RADIUS Alive SYSLOG SNMP
##
class Cisco_IOS_RADIUS_Alive_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS RADIUS Alive SYSLOG SNMP"
    event_class=RADIUSAlive
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^RADIUS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^RADIUS_ALIVE$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^RADIUS server (?P<ip>\S+):\d+,\d+ has returned\.$"),
    ]
##
## Cisco.IOS RADIUS Alive SYSLOG
##
class Cisco_IOS_RADIUS_Alive_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS RADIUS Alive SYSLOG"
    event_class=RADIUSAlive
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%RADIUS-4-RADIUS_ALIVE: RADIUS server (?P<ip>\S+):\d+,\d+ has returned\.$"),
    ]
##
## Cisco.IOS RADIUS Dead SYSLOG SNMP
##
class Cisco_IOS_RADIUS_Dead_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS RADIUS Dead SYSLOG SNMP"
    event_class=RADIUSDead
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^RADIUS_DEAD$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^RADIUS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^RADIUS server (?P<ip>\S+):\d+,\d+ is not responding\.$"),
    ]
##
## Cisco.IOS RADIUS Dead SYSLOG
##
class Cisco_IOS_RADIUS_Dead_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS RADIUS Dead SYSLOG"
    event_class=RADIUSDead
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%RADIUS-4-RADIUS_DEAD: RADIUS server (?P<ip>\S+):\d+,\d+ is not responding\.$"),
    ]
