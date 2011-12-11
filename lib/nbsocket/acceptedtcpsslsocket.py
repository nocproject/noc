# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import ssl
import logging
## NOC modules
from noc.lib.nbsocket.tcpsocket import TCPSocket
from noc.lib.nbsocket.acceptedtcpsocket import AcceptedTCPSocket


class AcceptedTCPSSLSocket(AcceptedTCPSocket):
    """
    SSL-aware version of AcceptedTCPSocket
    """
    def __init__(self, factory, socket, cert):
        socket = ssl.wrap_socket(socket, server_side=True,
                                 do_handshake_on_connect=False,
                                 keyfile=cert, certfile=cert,
                                 ssl_version=ssl.PROTOCOL_TLSv1)
        self.ssl_handshake_passed = False
        TCPSocket.__init__(self, factory, socket)

    def handle_read(self):
        """
        Process SSL handshake or incoming data
        """
        if self.ssl_handshake_passed:
            super(AcceptedTCPSSLSocket, self).handle_read()
        else:  # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed = True
                self.debug("SSL Handshake passed: %s" % str(self.socket.cipher()))
                self.handle_connect()  # handle_connect called after SSL negotiation
            except ssl.SSLError, err:
                if err.args[0] in (ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE):
                    # Incomplete handshake data
                    return
                logging.error("SSL Handshake failed: %s" % err[1])
                self.close()
