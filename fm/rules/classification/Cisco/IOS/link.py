# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,DROP_EVENT
from noc.fm.rules.classes.link import *
from noc.fm.rules.classes.default import DROP
##
## Cisco.IOS Link Up SNMP
##
class Cisco_IOS_Link_Up_SNMP(ClassificationRule):
    name="Cisco.IOS Link Up SNMP"
    event_class=LinkUp
    preference=2000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.4$"), # linkUp
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.\d+$",r"(?P<interface>.*)"),            # ifDescr
    ]
##
## Cisco.IOS Link Up Syslog SNMP
##
class Cisco_IOS_Link_Up_Syslog_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Link Up Syslog SNMP"
    event_class=LinkUp
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"), # clogMessageGenerated
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^LINK$"),                 # clogHistFacility
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^UPDOWN$"),               # clogHistMsgName
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^Interface (?P<interface>.+), changed state to up$"), # clogHistMsgText
    ]
##
## Cisco.IOS Link Up SYSLOG
##
class Cisco_IOS_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Link Up SYSLOG"
    event_class=LinkUp
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%LINK.*-3-UPDOWN: Interface (?P<interface>.+), changed state to up$"),
    ]
##
## Cisco.IOS Link Down SNMP
##
class Cisco_IOS_Link_Down_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Link Down SNMP"
    event_class=LinkDown
    preference=2000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.3$"), # linkDown
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.2\.\d+$",r"(?P<interface>.*)"),            # ifDescr
    ]
##
## Cisco.IOS Link Down Syslog SNMP
##
class Cisco_IOS_Link_Down_Syslog_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Link Down Syslog SNMP"
    event_class=LinkDown
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"), # clogMessageGenerated
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^LINK$"),                 # clogHistFacility
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^UPDOWN$"),               # clogHistMsgName
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^Interface (?P<interface>.+), changed state to down$"), # clogHistMsgText
    ]
##
## Cisco.IOS Link Down SYSLOG
##
class Cisco_IOS_Link_Down_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Link Down SYSLOG"
    event_class=LinkDown
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%LINK.*-3-UPDOWN: Interface (?P<interface>.+), changed state to down$"),
    ]
##
## Cisco.IOS Line Protocol SYSLOG
##
class Cisco_IOS_Line_Protocol_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Line Protocol SYSLOG"
    event_class=DROP
    preference=1000
    action=DROP_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%LINEPROTO-5-UPDOWN"),
    ]
