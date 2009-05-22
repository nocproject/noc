# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPsec correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.correlation import *
from noc.fm.rules.classes.ipsec import *

##
## IPsec Tunnel Start/Stop
##
class IPsec_Tunnel_Start_Stop_Rule(CorrelationRule):
    name="IPsec Tunnel Start/Stop"
    description=""
    rule_type="Pair"
    action=CLOSE_EVENT
    same_object=True
    window=0
    classes=[IPsecPhase1TunnelStart,IPsecPhase1TunnelStop,IPsecPhase2TunnelStart,IPsecPhase2TunnelStop]
    vars=["remote_ip","local_ip"]