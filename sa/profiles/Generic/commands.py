# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.icommands import ICommands


class Script(BaseScript):
    """
    Execute a list of CLI commands and return a list of results
    """
    name = "Generic.commands"
    interface = ICommands
    requires = []

    def execute(self, commands, ignore_cli_errors=False, include_commands=False):
        def safe_cli(c):
            try:
                return self.cli(c)
            # except self.CLISyntaxError, why:
            except self.CLISyntaxError as e:
                return "%%ERROR: %s" % e

        cli = safe_cli if ignore_cli_errors else self.cli
        r = []
        for c in commands:
            if include_commands:
                r += [c + "\n\n" + cli(c)]
            else:
                r += [cli(c)]
        return r
