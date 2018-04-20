# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network IO thread
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
## NOC modules
from noc.lib.nbsocket.socketfactory import SocketFactory
from snmp_get import SNMPGetSocket
from snmp_getnext import SNMPGetNextSocket
from snmp_count import SNMPCountSocket
from noc.lib.snmp.version import SNMP_v2c
from noc.lib.snmp.error import SNMPError

logger = logging.getLogger(__name__)


class IOThread(threading.Thread):
    def __init__(self, daemon):
        self._daemon = daemon
        self.factory = SocketFactory(
            controller=self,
            metrics_prefix=self._daemon.metrics + "io."
        )
        self.create_lock = threading.Lock()
        super(IOThread, self).__init__(name="io")

    def run(self):
        logger.info("Running I/O thread")
        self.factory.run(run_forever=True)

    def snmp_get(self, oids, address, port=161, community="public",
                 version=SNMP_v2c):
        logger.debug("SNMP GET [%s] %s" % (address, oids))
        with self.create_lock:
            s = SNMPGetSocket(self, oids, address, port,
                              community=community, version=version)
        r = s.get_result()
        if isinstance(r, SNMPError):
            logger.info("SNMP GET ERROR [%s] %s: code %s",
                        address, oids, r.code)
            raise r
        logger.debug("SNMP GET RESULT [%s] %s %s", address, oids, r)
        return r

    def snmp_getnext(self, oid, address, port=161, community="public",
                 version=SNMP_v2c, bulk=False):
        logger.debug("SNMP GETNEXT [%s] %s" % (address, oid))
        with self.create_lock:
            s = SNMPGetNextSocket(self, oid, address, port,
                                  community=community, version=version,
                                  bulk=False)
        for k, v in s.iter_result():
            logger.debug("SNMP GETNEXT RESULT [%s]: %s = %s",
                         address, k, v)
            yield k, v

    def snmp_count(self, oid, address, port=161, community="public",
                 version=SNMP_v2c, filter=None, bulk=False):
        logger.debug("SNMP GETNEXT COUNT [%s] %s" % (address, oid))
        with self.create_lock:
            s = SNMPCountSocket(self, oid, address, port,
                              community=community, version=version,
                              filter=filter, bulk=False)
        r = s.get_result()
        if isinstance(r, SNMPError):
            logger.info("SNMP GETNEXT COUNT ERROR [%s] %s: code %s",
                        address, oid, r.code)
            raise r
        logger.debug("SNMP GETNEXT COUNT RESULT [%s] %s %s",
                     address, oid, r)
        return r
