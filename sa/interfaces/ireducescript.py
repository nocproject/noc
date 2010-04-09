# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IReduceScript interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *
from noc.sa.scripts import ReduceScript
##
## Commonly accepted classes are:
## superuser, operator
## 
##
class IReduceScript(Interface):
    returns=InstanceOfParameter(cls=ReduceScript)
