# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import ICommands


class Script(NOCScript):
    """
    Execute a list of CLI commands and return a list of results
    """
    name = "Generic.commands"
    implements = [ICommands]
    requires = []

    def execute(self, commands, ignore_cli_errors=False):
        def safe_cli(c):
            try:
                return self.cli(c)
            except self.CLISyntaxError, why:
                return "%%ERROR: %s" % str(why)

        cli = safe_cli if ignore_cli_errors else self.cli
        return [cli(c) for c in commands]
