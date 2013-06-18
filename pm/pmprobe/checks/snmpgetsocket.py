## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMPGetSocket
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
## NOC modules
from noc.lib.nbsocket.udpsocket import UDPSocket
from noc.lib.snmp.get import get_pdu, parse_get_response


class SNMPGetSocket(UDPSocket):
    def __init__(self, check, address, port, timeout=10):
        self.check = check
        self.address = (address, port)
        super(SNMPGetSocket, self).__init__(self.check.get_factory())
        self.set_timeout(timeout)

    def get_request(self, community, oids):
        self.request_id = random.randint(0, 0x7FFFFFFF)
        self.community = community
        self.oids = set(oids)
        pdu = get_pdu(community, oids, self.request_id)
        self.sendto(pdu, self.address)

    def on_read(self, data, address, port):
        if (address, port) != self.address:
            return
        # Decode PDU and check request id
        response = parse_get_response(data)
        if (response.community == self.community and
                response.request_id == self.request_id):
            if response.error_status == 0:
                self.check.set_result(
                    dict((o, v) for o, v in response.varbinds
                         if o in self.oids))
            self.close()
