# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP server socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from protocol import STOMPProtocol
from noc.lib.nbsocket import AcceptedTCPSocket
from pdu import stomp_build_frame, VERSION
from noc.lib.debug import get_traceback


class STOMPServerSocket(AcceptedTCPSocket):
    protocol_class = STOMPProtocol

    def __init__(self, factory, socket, server=None):
        self.server = server
        print server
        AcceptedTCPSocket.__init__(self, factory, socket)

    def send_message(self, cmd, headers=None, body=""):
        msg = stomp_build_frame(cmd, headers, body)
        self.debug("Sending STOMP message:\n%s" % msg)
        self.write(msg)

    def send_error(self, headers, body=""):
        self.send_message("ERROR", headers, body)
        self.close(flush=True)

    def on_read(self, msg):
        cmd, headers, body = msg
        h = getattr(self, "cmd_%s" % cmd, None)
        if h:
            try:
                h(headers, body)
            except Exception:
                self.send_error(headers,
                    "Internal server error:\n%s" % get_traceback()
                )
                return
            # Send RECEIPT when requested
            if cmd != "CONNECT" and "receipt" in headers:
                self.send_message("RECEIPT", {
                    "receipt-id": headers["receipt"]})
        else:
            self.send_error(headers, "Invalid frame %s" % cmd)
            return

    def on_close(self):
        super(STOMPServerSocket, self).on_close()
        self.server.on_close(self)

    def cmd_CONNECT(self, headers, body):
        # Version negotiation (accept-version)
        if "accept-version" not in headers:
            self.send_error("No accepted-version")
            return
        versions = headers["accept-version"].split(",")
        if VERSION not in versions:
            self.send_error(headers,
                "Protocol version negotiation failed")
            return
        # @todo: host negotiation (host)
        # Authentication
        login = headers.get("login")
        passcode = headers.get("passcode")
        if not self.server.authenticate(login, passcode):
            self.send_error(headers, "Access denied")
            return
        # Send CONNECTED frame
        self.send_message("CONNECTED", {"version": VERSION})

    def cmd_SEND(self, headers, body):
        if "destination" not in headers:
            self.send_error(headers, "No 'destination' header")
            return
        self.server.send(headers["destination"], headers, body)

    def cmd_SUBSCRIBE(self, headers, body):
        if "destination" not in headers:
            self.send_error(headers, "No 'destination' header")
            return
        ack = headers.get("ack", "auto")
        if ack not in ("auto", "client", "client-individual"):
            self.send_error(headers, "Invalid ack mode: '%s'" % ack)
            return
        if "id" not in headers:
            self.send_error(headers, "No 'id' header")
            return
        self.server.subscribe(self, headers["id"],
            headers["destination"], ack)

    def cmd_UNSUBSCRIBE(self, headers, body):
        if "id" not in headers:
            self.send_error(headers, "No 'id' header")
            return
        self.server.unsubscribe(self, headers["id"])

    def cmd_ACK(self, headers, body):
        raise NotImplementedError

    def cmd_NACK(self, headers, body):
        raise NotImplementedError

    def cmd_BEGIN(self, headers, body):
        raise NotImplementedError

    def cmd_COMMIT(self, headers, body):
        raise NotImplementedError

    def cmd_DISCONNECT(self, headers, body):
        raise NotImplementedError