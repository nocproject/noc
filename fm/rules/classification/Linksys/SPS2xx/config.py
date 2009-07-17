# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys SPS2xx Configuraion-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.config import ConfigChanged
##
## Linksys.SPS2xx Config Changed SNMP
##
class Linksys_SPS2xx_Config_Changed_SNMP_Rule(ClassificationRule):
    name="Linksys.SPS2xx Config Changed SNMP"
    event_class=ConfigChanged
    preference=1000
    patterns=[
        (r"^source$",                                 r"^SNMP Trap$"),
        (r"^profile$",                                r"^Linksys\.SPS2xx$"),
        (r"^1\.3\.6\.1\.4\.1\.3955\.89\.2\.3\.2\.0$", r"^1$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",        r"^1\.3\.6\.1\.4\.1\.3955\.89\.0\.180$"),
    ]
