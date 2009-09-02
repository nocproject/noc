# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco AireOS 802.11 classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.dot11 import *
##
## Cisco.AireOS Roque AP Detected SNMP
##
class Cisco_AireOS_Roque_AP_Detected_SNMP_Rule(ClassificationRule):
    name="Cisco.AireOS Roque AP Detected SNMP"
    event_class=RogueAPDetected
    preference=1000
    required_mibs=["AIRESPACE-WIRELESS-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.AireOS$"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.7\.1\.1\.0$",r"^(?P<raw_mac>.+)$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.14179\.2\.6\.3\.36$"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.8\.1\.5\.0$",r"^(?P<channel>\d+)$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.8\.1\.4\.0$",r"^(?P<ap>.+)$"),
        Expression(r"mac",r"decode_mac(raw_mac)"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.8\.1\.6\.0$",r"^(?P<ssid>.*)$"),
    ]
##
## Cisco.AireOS Roque AP Removed SNMP
##
class Cisco_AireOS_Roque_AP_Removed_SNMP_Rule(ClassificationRule):
    name="Cisco.AireOS Roque AP Removed SNMP"
    event_class=RogueAPRemoved
    preference=1000
    required_mibs=["AIRESPACE-WIRELESS-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.AireOS$"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.7\.1\.1\.0$",r"^(?P<raw_mac>.+)$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.14179\.2\.6\.3\.41$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.14179\.2\.1\.8\.1\.4\.0$",r"^(?P<ap>.*)$"),
        Expression(r"mac",r"decode_mac(raw_mac)"),
    ]
