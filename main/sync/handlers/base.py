# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SyncHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
## NOC modules
from noc.lib.log import PrefixLoggerAdapter


class SyncHandler(object):
    type = None  # Set to handler type
    # DictParameter instance used to parse and clean config
    config = {}

    def __init__(self, daemon, name):
        self.daemon = daemon
        self.name = name
        self.logger = PrefixLoggerAdapter(daemon.logger, name)
        self.logger.info("Starting %s (%s)", name, self.type)
        self.cmd_queue = []

    def configure(self, **kwargs):
        pass

    def close(self):
        """
        Called when handler is closed
        """
        pass

    def on_create(self, uuid, data):
        """
        Object first seen
        """
        pass

    def on_delete(self, uuid):
        """
        Object removed
        """
        pass

    def on_change(self, uuid, data):
        """
        Object changed
        """
        pass

    def on_configuration_done(self):
        """
        End of configuration round
        """
        for c in self.cmd_queue:
            self.run_command(c)
        self.cmd_queue = []

    def get_command(self, cmd, **ctx):
        for v in ctx:
            cmd = cmd.replace("{%s}" % v, str(ctx[v]))
        return cmd

    def queue_command(self, cmd, once=False, **ctx):
        if not cmd:
            return
        cmd = self.get_command(cmd, **ctx)
        if not once or cmd not in self.cmd_queue:
            self.logger.debug("Queueing command: %s", cmd)
            self.cmd_queue += [cmd]

    def run_command(self, cmd, **ctx):
        """
        Run shell command with given context
        """
        if not cmd:
            return
        cmd = self.get_command(cmd, **ctx)
        self.logger.info("Running '%s'" % cmd)
        ret = subprocess.call(cmd, shell=True)
        if ret == 0:
            self.logger.debug("Success")
        else:
            self.logger.info("Failed (retcode %s)", ret)
