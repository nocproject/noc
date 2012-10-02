# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## One-time job to send sync request commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job


class SyncCtlJob(Job):
    name = "main.sync_request"
    threaded = False
    ignored = False

    def handler(self, *args, **kwargs):
        """
        data contains:
        {
            cmd: <command>,
            object: <object name>,
            channels: <channels to notify>
        }
        :param args:
        :param kwargs:
        :return:
        """
        msg = {"cmd": "request", "request": self.data["request"]}
        if "object" in self.data:
            msg["object"] = self.data["object"]
        for channel in self.data["channels"]:
            self.scheduler.daemon.send(
                msg, destination="/queue/sync/%s/" % channel)
        return True
