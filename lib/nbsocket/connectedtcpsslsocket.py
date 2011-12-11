# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ConnectedTCPSSLSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import ssl
## NOC modules
from noc.lib.nbsocket.connectedtcpsocket import ConnectedTCPSocket


class ConnectedTCPSSLSocket(ConnectedTCPSocket):
    """
    SSL-aware version of ConnectedTCPSocket
    """
    def __init__(self, factory, address, port, local_address=None):
        self.ssl_handshake_passed = False
        super(ConnectedTCPSSLSocket, self).__init__(factory, address, port,
                                                    local_address)

    def handle_connect(self):
        self.socket = ssl.wrap_socket(self.socket, server_side=False,
                                      do_handshake_on_connect=False,
                                      ssl_version=ssl.PROTOCOL_TLSv1)

    def handle_read(self):
        if self.ssl_handshake_passed:
            super(ConnectedTCPSSLSocket, self).handle_read()
        else:  # Process SSL Handshake
            try:
                self.socket.do_handshake()
                self.ssl_handshake_passed = True
                self.debug("SSL Handshake passed: %s" % str(
                    self.socket.cipher()))
            except ssl.SSLError, err:
                if err.args[0] in (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    # Incomplete handshake data
                    return
                raise
