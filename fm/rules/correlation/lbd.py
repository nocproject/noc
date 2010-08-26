# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LoopBack Detection correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classes.lbd import *
from noc.fm.rules.correlation import *
##
## LBD Loop Occured/Recovered
##
class LBD_Loop_Occured_Recovered_Rule(CorrelationRule):
    name="LBD Loop Occured/Recovered" 
    description="LBD Loop Occured/Recovered" 
    rule_type="Pair" 
    action=CLOSE_EVENT
    same_object=True
    window=0
    classes=[LBDLoopDetected,LBDLoopRecovered]
    vars=["vlan","interface"]