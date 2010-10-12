# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Security Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.security import *
##
## DLink.DES3xxx Login Success SYSLOG
##
class DLink_DES3xxx_Login_Success_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx Login Success SYSLOG"
    event_class=LoginSuccess
    preference=1000
    patterns=[
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"Successful login through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
    ]

##
## DLink.DES3xxx Logout SYSLOG
##
class DLink_DES3xxx_Logout_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx Logout SYSLOG"
    event_class=LoginClose
    preference=1000
    patterns=[
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
        (r"^message$",r"Logout through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
    ]

##
## DLink.DES3xxx Login Failed SYSLOG
##
class DLink_DES3xxx_Login_Failed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx Login Failed SYSLOG"
    event_class=LoginFailed
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^message$",r"Login failed through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
    ]

##
## DLink.DES3xxx Session timed out SYSLOG
##
class DLink_DES3xxx_Session_timed_out_SYSLOG_Rule(ClassificationRule):
    name="DLink.DES3xxx Session timed out SYSLOG"
    event_class=LoginClose
    preference=1000
    action=CLOSE_EVENT
    patterns=[
        (r"^message$",r"\S+ session timed out \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.D[EG]S3xxx$"),
    ]
