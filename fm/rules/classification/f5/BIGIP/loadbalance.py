# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5 loadbalancer's events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.loadbalance import *
##
## f5.BIGIP LB Pool Member Down SNMP
##
class f5_BIGIP_LB_Pool_Member_Down_SNMP_Rule(ClassificationRule):
    name="f5.BIGIP LB Pool Member Down SNMP"
    event_class=LBPoolMemberDown
    preference=1000
    required_mibs=["F5-BIGIP-COMMON-MIB"]
    patterns=[
        (r"^profile$",r"^f5\.BIGIP$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.2$",r"^(?P<node>\S+)$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.3$",r"^(?P<port>\d+)$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.1$",r"^Pool member \S+ monitor status down\.$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.0\.10$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
##
## f5.BIGIP LB Pool Member Up SNMP
##
class f5_BIGIP_LB_Pool_Member_Up_SNMP_Rule(ClassificationRule):
    name="f5.BIGIP LB Pool Member Up SNMP"
    event_class=LBPoolMemberUp
    preference=1000
    required_mibs=["F5-BIGIP-COMMON-MIB"]
    patterns=[
        (r"^profile$",r"^f5\.BIGIP$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.2$",r"^(?P<node>\S+)$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.3$",r"^(?P<port>\d+)$"),
        (r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.1\.1$",r"^Pool member \S+ monitor status up\.$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.3375\.2\.4\.0\.11$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
