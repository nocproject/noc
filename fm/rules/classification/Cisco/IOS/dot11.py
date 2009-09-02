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
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.",r"^Packet to client (?P<raw_mac>\S+) reached max retries, removing the client$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.",r"^DOT11$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.",r"^MAXRETRIES$"),
        Expression("mac","decode_mac(raw_mac)")
    ]
##
## Cisco.IOS Dot11 Deauthenticate SYSLOG
##
class Cisco_IOS_Dot11_Deauthenticate_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Dot11 Deauthenticate SYSLOG"
    event_class=Dot11Deauthenticate
    preference=1000
    patterns=[
        Expression(r"mac",r"decode_mac(raw_mac)"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%DOT11-6-DISASSOC: Interface Dot11Radio\d+, Deauthenticating Station (?P<raw_mac>\S+)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS WDS Auth Timeout SNMP
##
class Cisco_IOS_WDS_Auth_Timeout_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS WDS Auth Timeout SYSLOG SNMP"
    event_class=WDSAuthenticationTimeout
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^TIMEOUT$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^AP Timed out authenticating to the WDS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^LEAPCL$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
##
## Cisco.IOS WDS Auth Timeout SYSLOG
##
class Cisco_IOS_WDS_Auth_Timeout_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS WDS Auth Timeout SYSLOG"
    event_class=WDSAuthenticationTimeout
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%LEAPCL-3-TIMEOUT: AP Timed out authenticating to the WDS$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS CCMP Replay SNMP
##
class Cisco_IOS_CCMP_Replay_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS CCMP Replay SYSLOG SNMP"
    event_class=CCMPReplay
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^AES-CCMP TSC replay was detected on a packet \(TSC \S+\) received from (?P<raw_mac>\S+)\.$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^CCMP_REPLAY$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^DOT11$"),
        Expression(r"mac",r"decode_mac(raw_mac)"),
    ]
##
## Cisco.IOS CCMP Replay SYSLOG
##
class Cisco_IOS_CCMP_Replay_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS CCMP Replay SYSLOG"
    event_class=CCMPReplay
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%DOT11-4-CCMP_REPLAY: AES-CCMP TSC replay was detected on a packet \(TSC \S+\) received from (?P<raw_mac>\S+)\.$"),
        (r"^source$",r"^syslog$"),
        Expression(r"mac",r"decode_mac(raw_mac)"),
    ]
##
## Cisco.IOS dot11 Roamed SYSLOG
##
class Cisco_IOS_dot11_Roamed_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS dot11 Roamed SYSLOG"
    event_class=Dot11Roamed
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DOT11-6-ROAMED: Station (?P<raw_mac>\S+) Roamed to"),
        Expression(r"mac",r"decode_mac(raw_mac)"),
    ]
