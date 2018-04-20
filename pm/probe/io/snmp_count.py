# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP v2c GETNEXT socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
## NOC modules
from noc.lib.nbsocket.udpsocket import UDPSocket
from noc.lib.snmp.get import getnext_pdu, getbulk_pdu, parse_get_response
from noc.lib.snmp.consts import SNMP_v2c
from noc.lib.snmp.error import NO_ERROR, NO_SUCH_NAME, SNMPError

logger = logging.getLogger(__name__)


class SNMPCountSocket(UDPSocket):
    TTL = 5
    BULK_MAX_REPETITIONS = 20

    def __init__(self, io, oid, address, port=161,
                 community="public", version=SNMP_v2c, filter=None,
                 bulk=False):
        self.address = address
        self.port = port
        self.community = community
        self.oid = oid
        self.poid = oid + "."
        self.version = version
        self.result_event = threading.Event()
        self.result = 0
        self.is_error = False
        self.closed = False
        self.bulk = bulk
        if filter:
            self.filter = filter
        else:
            self.filter = lambda x, y: True
        super(SNMPCountSocket, self).__init__(io.factory)

    def get_label(self):
        return "%s %s" % (self.__class__.__name__, self.address)

    def get_pdu(self, oid):
        if self.bulk:
            return getbulk_pdu(
                self.community, oid,
                max_repetitions=self.BULK_MAX_REPETITIONS
            )
        else:
            return getnext_pdu(self.community, oid)

    def create_socket(self):
        super(SNMPCountSocket, self).create_socket()
        self.sendto(
            self.get_pdu(self.oid),
            (self.address, self.port)
        )

    def on_read(self, data, address, port):
        resp = parse_get_response(data)
        if resp.error_status == NO_SUCH_NAME:
            # NULL result
            self.close()
        elif resp.error_status != NO_ERROR:
            # Error
            self.result = SNMPError(code=resp.error_status, oid=self.oid)
            self.result_event.set()
            self.close()
        else:
            # Success value
            for k, v in resp.varbinds:
                if k.startswith(self.poid):
                    # Next value
                    if self.filter(k, v):
                        self.result += 1
                    # Next request
                    self.sendto(
                        self.get_pdu(k),
                        (self.address, self.port)
                    )
                else:
                    # Stop
                    self.close()

    def on_close(self):
        super(SNMPCountSocket, self).on_close()
        # Notify end of data
        self.result_event.set()

    def get_result(self):
        self.result_event.wait()
        return self.result
