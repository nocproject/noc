# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Telnet CLI
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
## NOC modules
from base import CLI


class BeefCLI(CLI):
    name = "beef"

    def __init__(self, *args, **kwargs):
        super(BeefCLI, self).__init__(*args, **kwargs)
        self.beef = self.script.credentials["beef"]

    def execute(self, cmd):
        scm = self.script.profile.command_submit
        if cmd.endswith(self.script.profile.command_submit):
            c = cmd[:-len(scm)]
        else:
            c = cmd
        try:
            result = self.beef.cli[c]
        except KeyError:
            raise self.CLIError(cmd)
        # Strip echo
        if result.startswith(cmd):
            result = result[len(cmd):]
        #
        return result
