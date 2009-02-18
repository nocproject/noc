# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS-specific QoS Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Cisco.IOS Auto-QoS Trust Device Detected
##
class CiscoIOSAutoQoSTrustDeviceDetected(EventClass):
    name     = "Cisco.IOS AutoQoS Trust Device Detected"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="Auto-QoS Trust Device Detected: {{interface}}"
    body_template="""Auto-QoS detected trusted device {{device}} on {{interface}}. Setting port to trusted"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    class Vars:
        interface=Var(required=True)
        device=Var(required=False)
##
## Cisco.IOS Auto-QoS Trust Device Detected
##
class CiscoIOSAutoQoSTrustDeviceLost(EventClass):
    name     = "Cisco.IOS AutoQoS Trust Device Lost"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="Auto-QoS Trust Device Lost: {{interface}}"
    body_template="""Auto-QoS lost trusted device {{device}} on {{interface}}. Setting port to untrusted"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    class Vars:
        interface=Var(required=True)
        device=Var(required=False)
