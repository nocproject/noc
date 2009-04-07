# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS LDP-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression
from noc.fm.rules.classes.ldp import *

##
## Juniper.JUNOS LDP LSP Up SNMP
##
class Juniper_JUNOS_LDP_LSP_Up_SNMP_Rule(ClassificationRule):
    name="Juniper.JUNOS LDP LSP Up SNMP"
    event_class=LDPLSPUp
    preference=1000
    required_mibs=["JUNIPER-LDP-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Juniper\.JUNOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.2636\.4\.4\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.2636\.3\.14\.1\.1\.\d+$",r"^(?P<bin_fec>.+)$"),
        (r"^1\.3\.6\.1\.4\.1\.2636\.3\.14\.1\.2\.\d+$",r"^(?P<bin_router_id>.+)$"),
        Expression("fec","decode_ipv4(bin_fec)"),
        Expression("router_id","decode_ipv4(bin_router_id)"),
    ]
    
##
## Juniper.JUNOS LDP LSP Down SNMP
##
class Juniper_JUNOS_LDP_LSP_Down_SNMP_Rule(ClassificationRule):
    name="Juniper.JUNOS LDP LSP Down SNMP"
    event_class=LDPLSPDown
    preference=1000
    required_mibs=["JUNIPER-LDP-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Juniper\.JUNOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.2636\.4\.4\.0\.2$"),
        (r"^1\.3\.6\.1\.4\.1\.2636\.3\.14\.1\.1\.\d+$",r"^(?P<bin_fec>.+)$"),
        (r"^1\.3\.6\.1\.4\.1\.2636\.3\.14\.1\.2\.\d+$",r"^(?P<bin_router_id>.+)$"),
        Expression("fec","decode_ipv4(bin_fec)"),
        Expression("router_id","decode_ipv4(bin_router_id)"),
    ]
