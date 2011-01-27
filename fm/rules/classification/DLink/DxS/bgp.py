# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink DxS BGP-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.bgp import *

##
## DLink.DxS BGP Established SYSLOG
##
class DLink_DxS_BGP_Established_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS BGP Established SYSLOG"
    event_class=BGPEstablished
    preference=1000
    patterns=[
        (r"^message$",r"\[BGP\(\d+\):\] BGP connection is successfully established (\()?Peer:\<(?P<neighbor_ip>\S+)\>(\))?."),
        (r"^source$", r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
##
## DLink.DxS BGP Closed SYSLOG
##
class DLink_DxS_BGP_Closed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS BGP Closed SYSLOG"
    event_class=BGPNeighborShutdown
    preference=1000
    patterns=[
        (r"^message$",r"\[BGP\(\d+\):\] BGP connection is normally closed (\()?Peer:\<(?P<neighbor_ip>\S+)\>(\))?."),
        (r"^source$", r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
