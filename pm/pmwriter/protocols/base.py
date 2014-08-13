## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMWriter collector socket base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nbsocket.acceptedtcpsocket import AcceptedTCPSocket


class PMCollectorTCPSocket(AcceptedTCPSocket):
    # Override protocol class
    protocol_class = None

    def __init__(self, factory, socket):
        self.server = factory.controller
        super(PMCollectorTCPSocket, self).__init__(factory, socket)

    def on_read(self, msg):
        """
        Parsed PDU is (metric, value, timestamp)
        """
        self.server.register_metric(*msg)
