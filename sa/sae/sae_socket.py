# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE RPC Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nbsocket import AcceptedTCPSocket
from noc.sa.rpc import RPCSocket
from noc.sa.models import Activator
from noc.sa.protocols.sae_pb2 import *
from noc.lib.ip import IP


class SAESocket(RPCSocket, AcceptedTCPSocket):
    """
    AcceptedTCPSocket with SAE RPC protocol
    """
    def __init__(self, factory, socket):
        AcceptedTCPSocket.__init__(self, factory, socket)
        RPCSocket.__init__(self, factory.sae.service)
        self.nonce = None
        self.is_authenticated = False
        self.pool_name = None
        
    @classmethod
    def check_access(cls, address):
        # @todo: Check via SAE
        return Activator.check_ip_access(address)
    
    def close(self):
        # Rollback all active transactions
        e = Error(code=ERR_ACTIVATOR_LOST,
                  text="Connection with activator lost")
        self.transactions.rollback_all_transactions(e)
        super(AcceptedTCPSocket, self).close()
    
    def set_pool_name(self, name):
        self.pool_name = name
    
    def on_close(self):
        if self.is_authenticated:
            self.factory.sae.leave_activator_pool(self.pool_name, self)
