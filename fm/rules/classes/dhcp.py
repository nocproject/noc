# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DHCP client/server events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## DHCPD Address Conflict
##
class DHCPDAddressConflict(EventClass):
    name     = "DHCPD Address Conflict"
    category = "NETWORK"
    priority = "WARNING"
    subject_template="DHCPD detects address conflict: {{ip}}"
    body_template="""DHCPD detects address conflict: {{ip}}"""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=False)
