# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PM Collector socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.protocols.pm_pb2 import PMMessage
from noc.lib.pmhash import pmhash


class PMCollectorSocket(ListenUDPSocket):
    """
    PM Collector socket
    """
    def __init__(self, activator, address, port):
        self.activator = activator
        super(PMCollectorSocket, self).__init__(activator.factory,
                                                address, port)

    def on_read(self, data, address, port):
        msg = PMMessage()
        try:
            msg.ParseFromString(data)
        except: # @todo: specify exact type of exception
            return
        # Check hash
        if pmhash(address, self.activator.pm_data_secret,
                  ([d.timestamp for d in msg.result] +
                    [d.timestamp for d in msg.data])) != msg.checksum:
            logging.error("Invalid PM hash in packet from %s" % address)
            return
        # Queue data
        self.activator.queue_pm_result([(d.probe_name, d.probe_type,
                                         d.timestamp, d.service, d.result,
                                         d.message)
                                         for d in msg.result
                                         if d.probe_name])
        self.activator.queue_pm_data([(d.name, d.timestamp, d.is_null, d.value)
                                       for d in msg.data if d.name])
