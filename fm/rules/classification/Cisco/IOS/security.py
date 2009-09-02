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
        (r"^message$",r"%SEC-6-IPACCESSLOGP: list (?P<acl_name>.+?) denied (?P<proto>\S+) (?P<src_ip>\S+)\((?P<src_port>\d+)\) (?:\(.*\) )?-> (?P<dst_ip>\S+)\((?P<dst_port>\d+)\), (?P<count>\d+) packets?$"),
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
##
## Cisco.IOS Login Success SYSLOG
##
class Cisco_IOS_Login_Success_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Login Success SYSLOG"
    event_class=LoginSuccess
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SEC_LOGIN-5-LOGIN_SUCCESS: Login Success \[user: (?P<user>.*?)\] \[Source: (?P<ip>\S+)\] \[localport: \d+\]"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS Login Failed SYSLOG SNMP
##
class Cisco_IOS_Login_Failed_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Login Failed SYSLOG SNMP"
    event_class=LoginFailed
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^SEC_LOGIN$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^Login failed \[user: (?P<user>.*?)\] \[Source: (?P<ip>\S+)\] \[localport: 22\] \[Reason: Login Authentication Failed\]"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^LOGIN_FAILED$"),
    ]
##
## Cisco.IOS Login Failed SYSLOG
##
class Cisco_IOS_Login_Failed_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Login Failed SYSLOG"
    event_class=LoginFailed
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SEC_LOGIN-4-LOGIN_FAILED: Login failed \[user: (?P<user>.*?)\] \[Source: (?P<ip>\S+)\] \[localport: \d+\] \[Reason: Login Authentication Failed\]"),
        (r"^source$",r"^syslog$"),
    ]
##
## Cisco.IOS SSH Other SYSLOG
##
class Cisco_IOS_SSH_Other_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS SSH Other SYSLOG"
    event_class=DROP
    preference=1000
    action=DROP_EVENT
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SSH-5-SSH2_(?:USERAUTH|SESSION|CLOSE)"),
        (r"^source$",r"^syslog$"),
    ]
