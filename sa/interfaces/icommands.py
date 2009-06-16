# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface to execute series of commands and return a list of results
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class ICommands(Interface):
    commands=StringListParameter()
    returns=StringListParameter()
