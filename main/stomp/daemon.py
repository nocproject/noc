# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-stomp daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import time
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.nbsocket import SocketFactory
from noc.lib.stomp.serversocket import STOMPServerSocket
from noc.main.models.stompaccess import StompAccess
from subscription import Subscription
from destination import Destination
from storage import Storage


class STOMPDaemon(Daemon):
    daemon_name = "noc-stomp"

    def __init__(self):
        super(STOMPDaemon, self).__init__()
        logging.info("Running noc-stomp")
        self.factory = SocketFactory(controller=self, write_delay=False)
        self.subscriptions = {}  # socket, id -> Subscription
        self.destinations = {}  # name -> destination
        self.storage = Storage()

    # def load_config(self):
    #    super(STOMPDaemon, self).load_config()

    def authenticate(self, login, passcode, address):
        if StompAccess.authenticate(login, passcode, address):
            logging.info("%s (%s): Authenticated" % (
                login, address))
            return True
        else:
            logging.info("%s (%s): Authentication failed" % (
                login, address))
            return False

    def run(self):
        self.factory.listen_tcp(
            self.config.get("stomp", "listen"),
            self.config.getint("stomp", "port"),
            STOMPServerSocket
        )
        self.factory.run()

    def get_destination(self, name):
        if name not in self.destinations:
            logging.info("Opening destination '%s'" % name)
            d = Destination(self, name)
            self.destinations[name] = d
        return self.destinations[name]

    def subscribe(self, socket, id, destination_name, ack):
        if (socket, id) in self.subscriptions:
            return
        d = self.get_destination(destination_name)
        s = Subscription(self, socket, id, d, ack)
        self.subscriptions[socket, id] = s
        d.subscribe(s)

    def unsubscribe(self, socket, id):
        s = self.subscriptions.get((socket, id))
        if not s:
            return
        d = s.destination
        d.unsubscribe(s)
        del self.subscriptions[socket, id]
        if d.is_empty():
            logging.info("Closing destination '%s'" % d.name)
            del self.destinations[d.name]

    def send(self, destination_name, headers, body):
        # Check expiration
        expires = None
        now = time.time()
        if "expires" in headers:
            expires = (now + int(headers["expires"]) / 1000.0)
        #
        if destination_name not in self.destinations:
            if (headers.get("persistent") == "true" and
                destination_name.startswith("/queue/")):
                # Store persistent message
                logging.debug("Store persistent message for %s" % destination_name)
                self.storage.put(
                    destination_name, headers, body, expires=expires)
            return
        self.destinations[destination_name].send(
            headers, body, expires=expires)

    def on_close(self, socket):
        """
        Called on client socket close
        :param socket:
        :return:
        """
        s = [x for x in self.subscriptions if x[0] == socket]
        for sock, id in s:
            self.unsubscribe(sock, id)
