# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Default Event class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var

##
## Default event class assigned when no matching event class found
##
class Default(EventClass):
    name="DEFAULT"
##
## DROP
##
class DROP(EventClass):
    name     = "DROP"
    category = "DEFAULT"
    priority = "DEFAULT"
    subject_template="DROPPED EVENT"
    body_template="""DROPPED EVENT"""
