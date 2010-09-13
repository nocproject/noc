# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LoopBack Detection classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classes.lbd import *
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
##
## DLink.DES3xxx LBD Loop Recovered SYSLOG
##
class DLink_DES3xxx_LBD_Loop_Recovered_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx LBD Loop Recovered SYSLOG" 
    event_class=LBDLoopRecovered
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
        (r"^message$",r"Port\s(?P<interface>\d+)\s+(?:VID\s+(?P<vlan>\d+)\s+)?LBD\s(?:port\s+)?recovered"),
    ]
##
## DLink.DES3xxx LBD Loop Detected SYSLOG
##
class DLink_DES3xxx_LBD_Loop_Detected_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx LBD Loop Detected SYSLOG" 
    event_class=LBDLoopDetected
    preference=1000
    patterns=[
        (r"^message$",r"Port\s(?P<interface>\d+)\s+(?:VID\s+(?P<vlan>\d+)\s+)?LBD\sloop\soccurred"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
    ]
