# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LoopBack Detection classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## LBD Loop Detected
##
class LBDLoopDetected(EventClass):
    name     = "LBD Loop Detected" 
    category = "NETWORK" 
    priority = "MAJOR" 
    subject_template="LBD: loop detected in port {{interface}}{% if vlan %}, vlan {{vlan}}{% endif %}"
    body_template="""LBD: loop detected in port {{interface}}{% if vlan %}, vlan {{vlan}}{% endif %}""" 
    repeat_suppression=False
    repeat_suppression_interval=3600
    class Vars:
        vlan=Var(required=False,repeat=False)
        interface=Var(required=True,repeat=False)
##
## LBD Loop Recovered
##
class LBDLoopRecovered(EventClass):
    name     = "LBD Loop Recovered" 
    category = "NETWORK" 
    priority = "NORMAL" 
    subject_template="LBD: loop recovered in port {{interface}}{% if vlan %}, vlan {{vlan}}{% endif %}" 
    body_template="""LBD: loop recovered in port {{interface}}{% if vlan %}, vlan {{vlan}}{% endif %}""" 
    repeat_suppression=False
    repeat_suppression_interval=3600
    class Vars:
        vlan=Var(required=False,repeat=False)
        interface=Var(required=True,repeat=False)
