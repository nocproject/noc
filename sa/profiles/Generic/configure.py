# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.configure
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import ICommands
##
## Enter a configuration mode and execute a list of CLI commands. return a list of results
##
class Script(noc.sa.script.Script):
    name="Generic.commands"
    implements=[ICommands]
    requires=[]
    def execute(self,commands):
        with self.configure():
            r=[self.cli(c) for c in commands]
        self.save_config()
        return r

