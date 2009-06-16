# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import ICommands
##
## Execute a list of CLI commands and return a list of results
##
class Script(noc.sa.script.Script):
    name="Generic.commands"
    implements=[ICommands]
    requires=[]
    def execute(self,commands):
        return [self.cli(c) for c in commands]
