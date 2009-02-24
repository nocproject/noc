# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EIGRP Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## EIGRP Neighbor Up
##
class EIGRPNeighborUp(EventClass):
    name     = "EIGRP Neighbor Up"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="EIGRP Neighbor {{ip}} ({{interface}}) is up"
    body_template="""EIGRP Neighbor {{ip}} ({{interface}}) is up"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=False)
        interface=Var(required=True,repeat=False)
##
## EIGRP Neighbor Down
##
class EIGRPNeighborDown(EventClass):
    name     = "EIGRP Neighbor Down"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="EIGRP Neighbor {{ip}} ({{interface}}) is down"
    body_template="""EIGRP Neighbor {{ip}} ({{interface}}) is down"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=False)
        interface=Var(required=True,repeat=False)
