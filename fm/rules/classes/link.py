# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Small DSL for event class description
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Link UP
##
class LinkUp(EventClass):
    name="Link Up"
    category="NETWORK"
    priority="NORMAL"
    subject_template="Link Up: {{interface}}"
    body_template="""Link Up: {{interface}}"""
    class Vars:
        interface=Var(required=True)
##
## Link Down
##
class LinkDown(EventClass):
    name="Link Down"
    category="NETWORK"
    priority="MAJOR"
    subject_template="Link Down: {{interface}}"
    body_template="""Link Down: {{interface}}"""
    class Vars:
        interface=Var(required=True)

