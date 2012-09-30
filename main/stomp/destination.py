# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-stomp daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import random


class Destination(object):
    def __init__(self, daemon, name):
        self.daemon = daemon
        self.name = name
        self.subscriptions = []
        self.msg_id = 0
        if name.startswith("/topic/"):
            self.get_subscriptions = self.get_subscriptions_topic
        else:
            self.get_subscriptions = self.get_subscriptions_queue

    def get_message_id(self):
        self.msg_id += 1
        return str(self.msg_id)

    def get_subscriptions_topic(self):
        for s in self.subscriptions:
            yield s

    def get_subscriptions_queue(self):
        if self.subscriptions:
            yield random.choice(self.subscriptions)

    def subscribe(self, s):
        """
        :param s:
        :type s: Subscription
        :return:
        """
        if s not in self.subscriptions:
            self.subscriptions += [s]
            if len(self.subscriptions) == 1:
                # Replay stored messages
                for id, h, msg, expires in self.daemon.storage.get_messages(self.name):
                    self.send(h, msg, expires=expires)
                    self.daemon.storage.remove(id)

    def unsubscribe(self, s):
        """
        :param s:
        :type s: Subscription
        :return:
        """
        if s in self.subscriptions:
            self.subscriptions.remove(s)

    def send(self, headers, msg, expires=None):
        t = time.time()
        if expires < t:
            return
        h = headers.copy()  # @todo: python 2.5
        h["destination"] = self.name
        h["message-id"] = self.get_message_id()
        for s in self.get_subscriptions():
            s.send(h, msg)

    def is_empty(self):
        return not self.subscriptions
