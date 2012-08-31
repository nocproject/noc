# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP Client library
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
import time
import itertools
## NOC modules
from clientsocket import STOMPClientSocket
from noc.lib.nbsocket import SocketFactory


class STOMPClient(object):
    ACK_AUTO = "auto"
    ACK_CLIENT = "client"
    ACK_CLIENT_INDIVIDUAL = "client-individual"

    def __init__(self, host, port, login=None, passcode=None,
                 factory=None, client_id=None):
        self.shared_factory = factory is not None
        self.host = host
        self.port = port
        self.login = login
        self.passcode = passcode
        self.factory = factory or SocketFactory(write_delay=False)
        self.factory_thread = None
        self.client_id = client_id
        self.socket = None
        self.subscription_id = itertools.count()  # Subscription id generator
        self.receipt_id = itertools.count()  # Receipt id generator
        self.callbacks = {}  # Subscription id -> callback
        self.destinations = {}  # destination -> (id, ack)
        self.started = False  # Set to True when start() called
        self.current_frame = None
        self.connected = threading.Event()  # Set on CONNECTED frame
        self.disconnect_receipt = None
        self.receipt_event = threading.Event()  # Block until receipt
        self.last_receipt = None  # Last receipt id

    def __repr__(self):
        return "<STOMPClient %s:%s>" % (self.host, self.port)

    def debug(self, message):
        logging.debug("STOMP(%s:%s): %s" % (
            self.host, self.port, message))

    def on_sock_conn_refused(self):
        """
        Called when socket connection is refused
        :return:
        """
        self.socket = None
        self.connected.clear()
        self.debug("Connection refused")

    def on_sock_close(self):
        """
        Called when client socket is closed
        :return:
        """
        self.debug("Socket closed")
        self.socket = None
        self.connected.clear()
        time.sleep(1)
        self.start_connection()

    def on_connected(self):
        """
        Called when CONNECTED frame received
        :return:
        """
        self.connected.set()
        if self.current_frame:
            command, message, body = self.current_frame
            self.current_frame = None
            self.send_frame(command, message, body)
        if self.destinations:
            self.refresh_subscriptions()

    def start(self):
        """
        Start client
        :return:
        """
        self.debug("Starting client")
        self.started = True
        if not self.shared_factory:
            self.debug("Running client factory")
            self.factory_thread = threading.Thread(
                target=self.factory.run,
                name="stomp-factory", args=(True,))
            self.factory_thread.daemon = True
            self.factory_thread.start()

    def stop(self):
        """
        Stop client
        :return:
        """
        self.started = False
        if self.socket:
            self.disconnect()
        if self.factory_thread:
            self.factory_thread.join()

    def start_connection(self):
        """
        Initialize connection attempt
        :return:
        """
        self.debug("Starting connection")
        self.connecting = True
        self.socket = self.factory.connect_tcp(self.host, self.port,
            STOMPClientSocket)
        self.socket.set_client(self)

    def send_frame(self, command, headers, body=""):
        # Check socket is connected
        if not self.connected.isSet():
            if not self.current_frame:
                # Save current frame
                # Send when ready
                self.current_frame = (command, headers, body)
                self.start_connection()
                return
            else:
                self.connected.wait()
        # Pass frame to socket
        self.socket.send_frame(command, headers, body)

    def subscribe(self, destination, callback=None, ack=ACK_AUTO):
        sid = str(self.subscription_id.next())
        self.debug("subscribe %s (id=%s)" % (destination, sid))
        self.callbacks[sid] = callback
        self.destinations[destination] = (sid, ack)
        self.send_frame("SUBSCRIBE", {
            "destination": destination,
            "ack": ack,
            "id": sid
        })

    def unsubscribe(self, destination):
        sid, _ = self.destinations[destination]
        self.debug("unsubscribe %s (id=%s)" % (destination, sid))
        self.send_frame("UNSUBSCRIBE", {
            "id": sid
        })

    def send(self, message, destination,
             receipt=False, persistent=False):
        if self.last_receipt:
            self.receipt_event.wait()
        self.last_receipt = None
        self.debug("send (%s): %s" % (destination, message))
        h = {"destination": destination}
        if receipt:
            self.last_receipt = str(self.receipt_id.next())
            h["receipt"] = self.last_receipt
            self.receipt_event.clear()
        if persistent:
            h["persistent"] = "true"
        self.send_frame("SEND", h, message)

    def on_message(self, destination, sid, body):
        c = self.callbacks.get(sid)
        if c:
            c(destination, body)

    def wait(self):
        """Wait until factory completes"""
        if self.factory_thread:
            self.factory_thread.join()

    def refresh_subscriptions(self):
        """
        Refresh existing subscriptions
        :return:
        """
        for destination in self.destinations:
            sid, ack = self.destinations[destination]
            self.debug("Refreshing subscription to '%s'" % destination)
            self.send_frame("SUBSCRIBE", {
                "destination": destination,
                "ack": ack,
                "id": sid
            })

    def disconnect(self):
        self.disconnect_receipt = str(self.receipt_id.next())
        self.send_frame("DISCONNECT", {
            "receipt": self.disconnect_receipt
        })

    def on_receipt(self, receipt_id):
        if receipt_id == self.disconnect_receipt:
            # DISCONNECT RECEIPT accepted
            self.socket.close()
            if not self.shared_factory:
                self.factory.shutdown()
        elif self.last_receipt and receipt_id == self.last_receipt:
            self.receipt_event.set()


