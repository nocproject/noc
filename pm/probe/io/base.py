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
from noc.lib.snmp.version import SNMP_v2c

logger = logging.getLogger(__name__)


class IOThread(threading.Thread):
    def __init__(self, daemon):
        self._daemon = daemon
        self.factory = SocketFactory(controller=self)
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
        logger.debug("SNMP GET RESULT [%s] %s %s" % (address, oids, r))
        return r
