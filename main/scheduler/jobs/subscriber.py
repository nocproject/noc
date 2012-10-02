# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP Subscriber Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job


class SubscriberJob(Job):
    ignored = True
    destination = None  # STOMP destination

    def get_destination(self):
        return self.destination

    def send(self, message, destination,
             receipt=False, persistent=False, expires=None):
        self.scheduler.daemon.send(message, destination,
            receipt=receipt, persistent=persistent, expires=expires)

    def handler(self, destination, body):
        return False
