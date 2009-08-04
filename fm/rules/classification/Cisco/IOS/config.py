# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,DROP_EVENT,CLOSE_EVENT
from noc.fm.rules.classes.config import *
from noc.fm.rules.classes.default import DROP

##
## Cisco.IOS Config Changed SNMP
##
class Cisco_IOS_Config_Changed_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Config Changed SNMP"
    event_class=ConfigChanged
    preference=1000
    required_mibs=["CISCO-CONFIG-MAN-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.43\.2\.0\.1$"), # snmpTrapOID.0 == ciscoConfigManEvent
        (r"^1.3.6.1.4.1.9.9.43.1.1.6.1.5.\d+",r"3"), # ccmHistoryEventConfigDestination == running
        (r"^source$",r"^SNMP Trap$"),
    ]
##
## Cisco.IOS Config Event
## Drop all events except saving to running-config
##
class Cisco_IOS_Config_Event_Drop_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Config Event Drop SNMP"
    event_class=DROP
    preference=90000
    action=DROP_EVENT
    required_mibs=["CISCO-CONFIG-MAN-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.43\.2\.0\.1$"), # snmpTrapOID.0 == ciscoConfigManEvent
        (r"^source$",r"^SNMP Trap$"),
    ]
##
## Cisco.IOS Config Changed Syslog
##
class Cisco_IOS_Config_Changed_Syslog_Rule(ClassificationRule):
    name="Cisco.IOS Config Changed Syslog"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%SYS-5-CONFIG_I: Configured"),
    ]
##
## Cisco.IOS C4500 Config Synced SYSLOG
##
class Cisco_IOS_C4500_Config_Synced_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS C4500 Config Synced SYSLOG"
    event_class=ConfigSynced
    preference=1000
    action=CLOSE_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%C4K_REDUNDANCY-5-CONFIGSYNC:"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS Config Synced SYSLOG
##
class Cisco_IOS_Config_Synced_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Config Synced SYSLOG"
    event_class=ConfigSynced
    preference=1000
    action=CLOSE_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%PFINIT-SP-5-CONFIG_SYNC"),
        (r"^source$",r"^syslog$"),
    ]
