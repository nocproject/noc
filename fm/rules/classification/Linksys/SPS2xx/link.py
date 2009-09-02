# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.link import LinkUp, LinkDown
##
## Linksys.SPS2xx Link Up SNMP
##
class Linksys_SPS2xx_Link_Up_SNMP_Rule(ClassificationRule):
    name="Linksys.SPS2xx Link Up SNMP"
    event_class=LinkUp
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",                            r"^SNMP Trap$"),
        (r"^profile$",                           r"^Linksys\.SPS2xx$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",   r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.4$"),
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.1\.\d+$", r"(?P<interface>.*)"),
    ]
##
## Linksys.SPS2xx Link Down SNMP
##
class Linksys_SPS2xx_Link_Down_SNMP_Rule(ClassificationRule):
    name="Linksys.SPS2xx Link Down SNMP"
    event_class=LinkDown
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^source$",                            r"^SNMP Trap$"),
        (r"^profile$",                           r"^Linksys\.SPS2xx$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",   r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.3$"),
        (r"^1\.3\.6\.1\.2\.1\.2\.2\.1\.1\.\d+$", r"(?P<interface>.*)"),
    ]
