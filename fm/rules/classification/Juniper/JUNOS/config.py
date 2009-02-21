# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.config import *
##
## Juniper.JUNOS Config Changed SNMP
##
class Juniper_JUNOS_Config_Changed_SNMP_Rule(ClassificationRule):
    name="Juniper.JUNOS Config Changed SNMP"
    event_class=ConfigChanged
    preference=1000
    required_mibs=["JUNIPER-CFGMGMT-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Juniper\.JUNOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.2636\.4\.5\.0\.1$"), # jnxCmCfgChange
    ]
##
## Juniper.JUNOS Config Changed CM SNMP
##
class Juniper_JUNOS_Config_Changed_CM_SNMP_Rule(ClassificationRule):
    name="Juniper.JUNOS Config Changed CM SNMP"
    event_class=ConfigChanged
    preference=1000
    required_mibs=["JUNIPER-CFGMGMT-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Juniper\.JUNOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.2636\.4\.5$"),
        (r"^1\.3\.6\.1\.4\.1\.2636\.3\.18\.1\.7\.1\.5\.\d+$",r"^(?P<user>.*)$"),
    ]
