# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 802.11 WI-FI events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## A station associated to an access point.
##
class Dot11Associated(EventClass):
    name="dot11 Associated"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station associated: {{mac}}"
    body_template="dot11 station associated: {{mac}}"
    class Vars:
        mac=Var(required=True)

##
## A station disassociated from an access point.
##
class Dot11Disassociated(EventClass):
    name="dot11 Disassociated"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station disassociated: {{mac}}"
    body_template="dot11 station disassociated: {{mac}}"
    class Vars:
        mac=Var(required=True)
##
## A station has roamed to a new access point.
##
class Dot11Roamed(EventClass):
    name="dot11 Roamed"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 station roamed: {{mac}}"
    body_template="dot11 station roamed: {{mac}}"
    class Vars:
        mac=Var(required=True)
##
##
##
class Dot11Deauthenticate(EventClass):
    name="dot11 Deauthenticate"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 deauthenticate: {{mac}}"
    body_template="dot11 deauthenticate: {{mac}}"
    class Vars:
        mac=Var(required=True)
##
## Too many retries to client
##
class Dot11MaxRetries(EventClass):
    name="dot11 Max Retries"
    category="NETWORK"
    priority="INFO"
    subject_template="dot11 Too Many Retries: {{mac}}"
    body_template="dot11 Too many retries: {{mac}}. Removing the client"
    class Vars:
        mac=Var(required=True)
##
## CCMP Replay
##
class CCMPReplay(EventClass):
    name     = "CCMP Replay"
    category = "SECURITY"
    priority = "MAJOR"
    subject_template="CCMP Replay attempt from: {{mac}}"
    body_template="""AES-CCMP TSC replay was indicated on a frame. A replay of the AES-CCMP TSC in a received packet almost indicates an active attack."""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        mac=Var(required=True,repeat=False)
##
## WDS Authentication Timeout
##
class WDSAuthenticationTimeout(EventClass):
    name     = "WDS Authentication Timeout"
    category = "NETWORK"
    priority = "MINOR"
    subject_template="WDS Authentication Timeout"
    body_template="""AP Timed out authenticating to the WDS"""
    repeat_suppression=False
    repeat_suppression_interval=0
    trigger=None
##
## Rogue AP Detected
##
class RogueAPDetected(EventClass):
    name     = "Rogue AP Detected"
    category = "SECURITY"
    priority = "WARNING"
    subject_template="Roque AP Detected by {{ap}}: {{mac}}"
    body_template="""Access Point {{ap}} has detected roque AP with MAC address {{mac}} at channel {{channel}}.
Rogue AP SSID is: {{ssid}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        mac=Var(required=True,repeat=False)
        ap=Var(required=False,repeat=False)
        channel=Var(required=False,repeat=False)
        ssid=Var(required=False,repeat=False)
##
## Rogue AP Removed
##
class RogueAPRemoved(EventClass):
    name     = "Rogue AP Removed"
    category = "SECURITY"
    priority = "NORMAL"
    subject_template="Roque AP Removed: {{mac}}@{{ap}}"
    body_template="""Roque AP {{mac}} has left {{ap}} area"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ap=Var(required=True,repeat=False)
        mac=Var(required=True,repeat=False)
