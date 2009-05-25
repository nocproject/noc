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
## Cisco.IOS ACL Reject SYSLOG
##
class Cisco_IOS_ACL_Reject_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS ACL Reject SYSLOG"
    event_class=ACLReject
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SEC-6-IPACCESSLOGP: list (?P<acl_name>.+?) denied (?P<proto>\S+) (?P<src_ip>\S+)\((?P<src_port>\d+)\) \(.*\) -> (?P<dst_ip>\S+)\((?P<dst_port>\d+)\), (?P<count>\d+) packets?$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS ACL Permit SYSLOG
##
class Cisco_IOS_ACL_Permit_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS ACL Permit SYSLOG"
    event_class=ACLPermit
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SEC-6-IPACCESSLOGP: list (?P<acl_name>.+?) permitted (?P<proto>\S+) (?P<src_ip>\S+)\((?P<src_port>\d+)\) -> (?P<dst_ip>\S+)\((?P<dst_port>\d+)\), (?P<count>\d+) packets?$"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS IPACCESSLOGRL SYSLOG
##
class Cisco_IOS_IPACCESSLOGRL_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS IPACCESSLOGRL SYSLOG"
    event_class=DROP
    preference=1000
    action=DROP_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SEC-6-IPACCESSLOGRL:"),
        (r"^source$",r"^syslog$"),
    ]
