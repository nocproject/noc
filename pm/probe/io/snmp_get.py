# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP v2c GET socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
## NOC modules
from noc.lib.nbsocket.udpsocket import UDPSocket
from noc.lib.snmp.get import get_pdu, parse_get_response
from noc.lib.snmp.version import SNMP_v2c
from noc.lib.snmp.error import NO_ERROR, SNMPError

logger = logging.getLogger(__name__)


class SNMPGetSocket(UDPSocket):
    TTL = 5

    def __init__(self, io, oids, address, port=161,
                 community="public", version=SNMP_v2c):
        self.address = address
        self.port = port
        self.community = community
        self.oids = oids
        self.version = version
        self.oid_map = {}
        if isinstance(oids, basestring):
            oids = [oids]
        elif isinstance(oids, dict):
            oids = self.oids.values()
            self.oid_map = dict((self.oids[k], k) for k in self.oids)
        else:
            raise ValueError("oids must be either string or dict")
        self.pdu = get_pdu(community, oids)
        self.result_event = threading.Event()
        self.result = None
        super(SNMPGetSocket, self).__init__(io.factory)

    def create_socket(self):
        super(SNMPGetSocket, self).create_socket()
        self.sendto(self.pdu, (self.address, self.port))

    def on_read(self, data, address, port):
        resp = parse_get_response(data)
        if resp.error_status != NO_ERROR:
            oid = None
            if resp.error_index and resp.varbinds:
                oid = resp.varbinds[resp.error_index - 1][0]
            self.result = SNMPError(code=resp.error_status, oid=oid)
        else:
            # Success
            if self.oid_map:
                self.result = {}
                for k, v in resp.varbinds:
                    if k in self.oid_map:
                        self.result[self.oid_map[k]] = v
            else:
                self.result = resp.varbinds[0][1]
        self.result_event.set()
        self.close()

    def on_close(self):
        super(SNMPGetSocket, self).on_close()
        self.result_event.set()

    def get_result(self):
        self.result_event.wait()
        return self.result
