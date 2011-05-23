# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator to SAE connection
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.rpc import RPCSocket
from noc.lib.nbsocket import ConnectedTCPSocket


class ActivatorSocket(RPCSocket, ConnectedTCPSocket):
    """
    Activator -> SAE connection
    """
    def __init__(self, factory, address, port, local_address=None):
        ConnectedTCPSocket.__init__(self, factory, address, port, local_address)
        RPCSocket.__init__(self, factory.controller.service)

    def activator_event(self, event):
        self.factory.controller.event(event)

    def on_connect(self):
        self.activator_event("connect")

    def on_close(self):
        self.activator_event("close")

    def on_conn_refused(self):
        self.activator_event("refused")
