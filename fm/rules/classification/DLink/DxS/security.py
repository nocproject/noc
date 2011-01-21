# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Security Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.security import *
##
## DLink.DES3xxx Login Success SYSLOG
##
class DLink_DxS_Login_Success_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Login Success SYSLOG"
    event_class=LoginSuccess
    preference=1000
    patterns=[
        (r"^message$",r"Successful login through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]

##
## DLink.DxS Logout SYSLOG
##
class DLink_DxS_Logout_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Logout SYSLOG"
    event_class=LoginClose
    preference=1000
    patterns=[
        (r"^message$",r"Logout through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]

##
## DLink.DxS Login Failed SYSLOG
##
class DLink_DxS_Login_Failed_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Login Failed SYSLOG"
    event_class=LoginFailed
    preference=1000
    patterns=[
        (r"^message$",r"Login failed through \S+ \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]

##
## DLink.DxS Session timed out SYSLOG
##
class DLink_DxS_Session_timed_out_SYSLOG_Rule(ClassificationRule):
    name="DLink.DxS Session timed out SYSLOG"
    event_class=LoginClose
    preference=1000
    action=CLOSE_EVENT
    patterns=[
        (r"^message$",r"\S+ session timed out \(Username: (?P<user>\S+)(?:, IP: (?P<ip>\S+))?(?:, MAC: \S+)?\)"),
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^DLink\.DxS$"),
    ]
