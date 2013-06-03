# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## XMPP notification channel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
## Third-party modules
import sleekxmpp
## NOC modules
from base import NotificationChannel
from noc.lib.validators import is_email


class XMPPClient(sleekxmpp.ClientXMPP):
    REPLIES = [
        "Mylord",
        "You are to me?",
        "Yes, mylord!",
        "Ready to serve",
        "Now what?",
        "More work?"
    ]

    def __init__(self, channel, jid, password):
        self.channel = channel
        super(XMPPClient, self).__init__(jid, password)
        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)
        self.register_plugin("xep_0030")  # Service discovery
        self.register_plugin("xep_0199")  # Ping

    def on_start(self):
        self.send_presence()
        self.get_roster()

    def on_message(self, msg):
        if msg["type"] in ("normal", "chat"):
            msg.reply(random.choice(self.REPLIES)).send()


class XMPPNotificationChannel(NotificationChannel):
    name = "xmpp"

    def __init__(self, daemon, instance, queue):
        super(XMPPNotificationChannel, self).__init__(
            daemon, instance, queue)
        self.client = None
        self.starting = False

    def on_start(self):
        self.info("Connecting as %s" % self.config.get("xmpp", "jid"))
        self.starting = True
        self.client = XMPPClient(
            self,
            self.config.get("xmpp", "jid"),
            self.config.get("xmpp", "password")
        )
        a = self.config.get("xmpp", "address")
        p = self.config.get("xmpp", "port")
        if a:
            address = (a, int(p) if p else 5222)
        else:
            address = tuple()
        if not self.client.connect(address):
            self.client = None
        self.starting = False
        self.client.process(block=False)

    def on_shutdown(self):
        if self.client:
            self.client._disconnect(wait=True)

    def send(self, to, subject, body, link=None):
        # Check client is ready
        if not self.client:
            if not self.starting:
                self.on_start()
            return False
        self.info("Sending '%s' to %s" % (subject, to))
        self.client.send_message(mto=to, mbody=body)
        return True
