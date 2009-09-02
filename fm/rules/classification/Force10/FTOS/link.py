# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS Link rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.link import *
##
## Force10.FTOS Link Up SYSLOG
##
class Force10_FTOS_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS Link Up SYSLOG"
    event_class=LinkUp
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^message$",r"%IFMGR-5-OSTATE_UP: Changed interface state to up: (?P<interface>.+)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Force10.FTOS Link Down SYSLOG
##
class Force10_FTOS_Link_Down_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS Link Down SYSLOG"
    event_class=LinkDown
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^message$",r"%IFMGR-5-OSTATE_DN: Changed interface state to down: (?P<interface>.+)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Force10.FTOS Link Up SNMP
##
class Force10_FTOS_Link_Up_SNMP_Rule(ClassificationRule):
    name="Force10.FTOS Link Up SNMP"
    event_class=LinkUp
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.4$"),
        (r"^1\.3\.6\.1\.4\.1\.6027\.3\.1\.1\.4\.1\.2$",r"^OSTATE_UP: Changed interface state to up: (?P<interface>.+)$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
##
## Force10.FTOS Link Down SNMP
##
class Force10_FTOS_Link_Down_SNMP_Rule(ClassificationRule):
    name="Force10.FTOS Link Down SNMP"
    event_class=LinkDown
    preference=1000
    required_mibs=["IF-MIB"]
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.6\.3\.1\.1\.5\.3$"),
        (r"^1\.3\.6\.1\.4\.1\.6027\.3\.1\.1\.4\.1\.2$",r"^OSTATE_DN: Changed interface state to down: (?P<interface>.+)$"),
        (r"^source$",r"^SNMP Trap$"),
    ]
