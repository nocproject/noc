# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNS-related events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## Bad DNS Query
##
class BadDNSQuery(EventClass):
    name     = "Bad DNS Query"
    category = "SECURITY"
    priority = "MAJOR"
    subject_template="Bad DNS Query from: {{ip}}"
    body_template="""Bad DNS Query from: {{ip}}"""
    repeat_suppression=True
    repeat_suppression_interval=600
    trigger=None
    class Vars:
        ip=Var(required=True,repeat=True)
