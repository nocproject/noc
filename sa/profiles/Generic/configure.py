# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.configure
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.icommands import ICommands


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Generic.configure
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import ICommands


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Enter a configuration mode and execute a list of CLI commands.
    return a list of results
    """
    name = "Generic.configure"
<<<<<<< HEAD
    interface = ICommands
=======
    implements = [ICommands]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    requires = []

    def execute(self, commands, ignore_cli_errors=False):
        def safe_cli(c):
            try:
                return self.cli(c)
<<<<<<< HEAD
            except self.CLISyntaxError as e:
                return "%%ERROR: %s" % e
=======
            except self.CLISyntaxError, why:
                return "%%ERROR: %s" % str(why)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        cli = safe_cli if ignore_cli_errors else self.cli
        with self.configure():
            r = [cli(c) for c in commands]
        self.save_config()
        return r
