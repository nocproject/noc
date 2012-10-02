# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Respond to STOMP requests
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from subscriber import SubscriberJob


class SyncJob(SubscriberJob):
    threaded = True
    ignored = False

    def handler(self, destination, body):
        cmd = body.get("cmd")
        channel = body.get("channel")
        if not cmd or not channel:
            return False
        if cmd == "list":
            return self.on_list(channel)
        elif cmd == "verify":
            objects = body.get("objects")
            if objects:
                r = True
                for o in objects:
                    r &= self.on_verify(channel, o)
                return r
        return False

    def on_list(self, channel):
        """
        LIST command handler
        :param channel:
        :param object:
        :return:
        """
        return False

    def on_verify(self, channel, object):
        """
        VERIFY command handler
        :param channel:
        :param object:
        :return:
        """
        return False
