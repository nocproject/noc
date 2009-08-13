# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.config import *
##
## Config Changed
##
class Config_Changed_Rule(ClassificationRule):
    name="Config Changed"
    event_class=ConfigChanged
    preference=1000
    required_mibs=["ENTITY-MIB"]
    patterns=[
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.2\.1\.47\.2\.0\.1$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
