# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS FreeBSD Security-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.security import *

##
## OS.FreeBSD IPFW Deny SYSLOG
##
class OS_FreeBSD_IPFW_Deny_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD IPFW Deny SYSLOG"
    event_class=ACLReject
    preference=1000
    patterns=[
        (r"^message$",r"ipfw: (?P<acl_name>\d+) Deny (?P<proto>\S+) (?P<src_ip>\S+):(?P<src_port>\d+) (?P<dst_ip>\S+):(?P<dst_port>\d+) (in|out) via \S+"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]

##
## OS.FreeBSD IPFW Accept SYSLOG
##
class OS_FreeBSD_IPFW_Accept_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD IPFW Accept SYSLOG"
    event_class=ACLPermit
    preference=1000
    patterns=[
        (r"^message$",r"ipfw: (?P<acl_name>\d+) Accept (?P<proto>\S+) (?P<src_ip>\S+):(?P<src_port>\d+) (?P<dst_ip>\S+):(?P<dst_port>\d+) (in|out) via \S+"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]

##
## OS.FreeBSD Login Failed SYSLOG
##
class OS_FreeBSD_Login_Failed_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD Login Failed SYSLOG"
    event_class=LoginFailed
    preference=1000
    patterns=[
        (r"^message$",r"error: PAM: authentication error for (illegal user )?(?P<user>.*?) from (?P<ip>\S+)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]

##
## OS.FreeBSD Login Success SYSLOG
##
class OS_FreeBSD_Link_Up_SYSLOG_Rule(ClassificationRule):
    name="OS.FreeBSD Login Success SYSLOG"
    event_class=LoginSuccess
    preference=1000
    patterns=[
        (r"^message$",r"Accepted keyboard\-interactive\/pam for (?P<user>\S+?) from (?P<ip>\S+) port \d+ \S+"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^OS\.FreeBSD$"),
    ]
