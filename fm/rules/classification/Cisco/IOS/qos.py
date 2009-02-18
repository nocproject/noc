# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## QoS classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.Cisco.IOS.qos import *
##
## Cisco.IOS AutoQoS Trust Device Detected SYSLOG
##
class Cisco_IOS_AutoQoS_Trust_Device_Detected_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS AutoQoS Trust Device Detected SYSLOG"
    event_class=CiscoIOSAutoQoSTrustDeviceDetected
    preference=1000
    patterns=[
        (r"^message$",r"%SWITCH_QOS_TB-5-TRUST_DEVICE_DETECTED: (?P<device>.+?) detected on port (?P<interface>.+?),"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS AutoQoS Trust Device Lost SYSLOG
##
class Cisco_IOS_AutoQoS_Trust_Device_Lost_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS AutoQoS Trust Device Lost SYSLOG"
    event_class=CiscoIOSAutoQoSTrustDeviceLost
    preference=1000
    patterns=[
        (r"^message$",r"%SWITCH_QOS_TB-5-TRUST_DEVICE_LOST: (?P<device>.+?) no longer detected on port (?P<interface>.+?),"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
    ]
