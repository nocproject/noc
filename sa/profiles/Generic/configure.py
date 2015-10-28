# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.configure
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import ICommands


class Script(BaseScript):
    """
    Enter a configuration mode and execute a list of CLI commands.
    return a list of results
    """
    name = "Generic.configure"
    interface = ICommands
    requires = []

    def execute(self, commands, ignore_cli_errors=False):
        def safe_cli(c):
            try:
                return self.cli(c)
            except self.CLISyntaxError, why:
                return "%%ERROR: %s" % str(why)

        cli = safe_cli if ignore_cli_errors else self.cli
        with self.configure():
            r = [cli(c) for c in commands]
        self.save_config()
        return r
