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


class SNMPGetNextSocket(UDPSocket):
    TTL = 5
    BULK_MAX_REPETITIONS = 20

    def __init__(self, io, oid, address, port=161,
                 community="public", version=SNMP_v2c, bulk=False):
        self.address = address
        self.port = port
        self.community = community
        self.oid = oid
        self.poid = oid + "."
        self.version = version
        self.result_condition = threading.Condition()
        self.result = []
        self.is_error = False
        self.closed = False
        self.bulk = bulk
        super(SNMPGetNextSocket, self).__init__(io.factory)

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
        super(SNMPGetNextSocket, self).create_socket()
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
            self.result_condition.acquire()
            self.is_error = True
            self.result = SNMPError(code=resp.error_status, oid=self.oid)
            self.result_condition.notify()
            self.result_condition.release()
            self.close()
        else:
            # Success value
            for k, v in resp.varbinds:
                if k.startswith(self.poid):
                    # Next value
                    self.result_condition.acquire()
                    self.result += [(k, v)]
                    self.result_condition.notify()
                    self.result_condition.release()
                    # Next request
                    self.sendto(
                        self.get_pdu(k),
                        (self.address, self.port)
                    )
                else:
                    # Stop
                    self.close()

    def on_close(self):
        super(SNMPGetNextSocket, self).on_close()
        # Notify end of data
        self.closed = True
        self.result_condition.acquire()
        self.result_condition.notify()
        self.result_condition.release()

    def iter_result(self):
        while True:
            self.result_condition.acquire()
            self.result_condition.wait()
            result = self.result
            self.result = []
            to_close = self.closed
            is_error = self.is_error
            self.result_condition.release()
            if is_error:
                raise result
            for r in result:
                yield r
            if to_close:
                break
