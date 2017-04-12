# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.configure
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.icommands import ICommands


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
            except self.CLISyntaxError as e:
                return "%%ERROR: %s" % e

        cli = safe_cli if ignore_cli_errors else self.cli
        with self.configure():
            r = [cli(c) for c in commands]
        self.save_config()
        return r
