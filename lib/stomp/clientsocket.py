# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP client socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from protocol import STOMPProtocol
from noc.lib.nbsocket import ConnectedTCPSocket
from pdu import stomp_build_frame, VERSION
from noc.lib.serialize import json_decode


class STOMPClientSocket(ConnectedTCPSocket):
    protocol_class = STOMPProtocol

    def set_client(self, client):
        self.client = client

    def send_frame(self, cmd, headers=None, body=""):
        msg = stomp_build_frame(cmd, headers, body)
        self.debug("Sending STOMP message:\n%s" % msg)
        self.write(msg)

    def on_read(self, msg):
        cmd, headers, body = msg
        h = getattr(self, "cmd_%s" % cmd, None)
        if h:
            h(headers, body)
        else:
            self.error("Unknown frame: '%s'" % cmd)

    def on_connect(self):
        # Send CONNECT frame
        self.send_frame("CONNECT", {
            "accept-version": VERSION,
            "host": self.address
        })

    def on_conn_refused(self):
        self.error("Connection refused")

    def cmd_ERROR(self, headers, body):
        self.error("STOMP error received: %s" % body)
        self.close()
        # @todo: push error

    def cmd_CONNECTED(self, headers, body):
        self.client.set_connected()

    def cmd_MESSAGE(self, headers, body):
        if "subscription" in headers and "destination" in headers:
            if headers.get("content-type") == "text/json":
                body = json_decode(body)
            self.client.on_message(
                headers["destination"], headers["subscription"], body)

    def subscribe(self, destination, id, ack):
        self.send_frame("SUBSCRIBE", {
            "destination": destination,
            "ack": ack,
            "id": id
        })

    def unsubscribe(self, id):
        self.send_frame("UNSUBSCRIBE", {
            "id": id
        })

    def send_message(self, msg, destination):
        self.send_frame("SEND", {
            "destination": destination
        }, msg)
