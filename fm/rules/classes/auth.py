# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Authentication Failed
##
class AuthenticationFailure(EventClass):
    name="Authentication Failure"
    category="SECURITY"
    priority="MAJOR"
    subject_template="Authentication failure from {{ip}}"
    body_template="""Authentication failure:
USER: {{user}}
IP: {{ip}}
"""
    class Vars:
        ip=Var(required=False)
        user=Var(required=False)
