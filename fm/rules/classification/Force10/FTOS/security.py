# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Security Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.security import *
from noc.fm.rules.classes.default import DROP

##
## Force10.FTOS Login Success SYSLOG
##
class Force10_FTOS_Login_Success_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS Login Success SYSLOG"
    event_class=LoginSuccess
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%SEC-5-LOGIN_SUCCESS: Login successful for user (?P<user>\S+) on line \S+ \((?P<ip>\S+)\)$"),
    ]
##
## Force10.FTOS Login Close SYSLOG
##
class Force10_FTOS_Login_Close_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS Login Close SYSLOG"
    event_class=LoginClose
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^message$",r"%SEC-5-LOGOUT: Exec session is terminated for user (?P<user>\S+) on line \S+ \((?P<ip>\S+)\)$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Force10.FTOS ACL Reject SYSLOG
##
class Force10_FTOS_ACL_Reject_SYSLOG_Rule(ClassificationRule):
    name="Force10.FTOS ACL Reject SYSLOG"
    event_class=ACLReject
    preference=1000
    patterns=[
        (r"^profile$",r"^Force10\.FTOS$"),
        (r"^message$",r"%PACKETLOG-6-(?:IN|E)GRESS_PKTLOG: L3 Deny.+IP Info: Proto=(?P<proto>\S+), SA=(?P<src_ip>\S+), DA=(?P<dst_ip>\S+), Len=\d+(?:, srcPort=(?P<src_port>\d+), dstPort=(?P<dst_port>\d+))?$"),
        (r"^source$",r"^syslog$"),
    ]
