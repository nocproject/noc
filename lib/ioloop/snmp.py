# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP methods implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import socket
import errno
## Third-party modules
from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from tornado.util import errno_from_exception
## NOC modules
from noc.lib.snmp.version import SNMP_v2c
from noc.lib.snmp.get import get_pdu, parse_get_response
from noc.lib.snmp.error import NO_ERROR, SNMPError, TIMED_OUT
from noc.lib.debug import error_report

_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)
logger = logging.getLogger(__name__)


def snmp_get(address, oids, port=161,
             community="public",
             version=SNMP_v2c,
             timeout=10,
             ioloop=None):
    """
    Perform SNMP get request and returns Future to be used
    inside @tornado.gen.coroutine
    """
    def on_event(fd, events):
        try:
            if events & IOLoop.WRITE:
                # Delayed send
                sock.sendto(pdu, (address, port))
                ioloop.update_handler(fd, IOLoop.READ)
            elif events & IOLoop.READ:
                # Process incoming PDU
                data, addr = sock.recvfrom(4096)
                ioloop.remove_handler(sock.fileno())
                sock.close()
                resp = parse_get_response(data)
                if resp.error_status != NO_ERROR:
                    oid = None
                    if resp.error_index and resp.varbinds:
                        oid = resp.varbinds[resp.error_index - 1][0]
                    logger.debug("[%s] SNMP error: %s %s",
                                 address, oid, resp.error_status)
                    try:
                        raise SNMPError(code=resp.error_status, oid=oid)
                    except SNMPError as e:
                        future.set_exception(e)
                else:
                    # Success
                    if oid_map:
                        result = {}
                        for k, v in resp.varbinds:
                            if k in oid_map:
                                result[oid_map[k]] = v
                    else:
                        result = resp.varbinds[0][1]
                    logger.debug("[%s] GET result %s",
                                 address, result)
                    future.set_result(result)
        except Exception as e:
            error_report()
            ioloop.remove_handler(sock.fileno())
            sock.close()

    def on_timeout():
        """
        Check future is not timed out
        """
        if future.running():
            logger.debug("[%s] SNMP GET timed out", address)
            ioloop.remove_handler(sock.fileno())
            sock.close()
            try:
                raise SNMPError(code=TIMED_OUT, oid=oids[0])
            except Exception as e:
                future.set_exception(e)

    oid_map = {}
    if isinstance(oids, basestring):
        oids = [oids]
    elif isinstance(oids, dict):
        oid_map = dict((oids[k], k) for k in oids)
        oids = oids.values()
    else:
        raise ValueError("oids must be either string or dict")
    logger.debug("[%s] SNMP GET %s", address, oids)
    ioloop = ioloop or IOLoop.current()
    pdu = get_pdu(community, oids)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    future = TracebackFuture()
    # Try to send data immediately
    try:
        sock.sendto(pdu, (address, port))
        ioloop.add_handler(
            sock.fileno(),
            on_event,
            IOLoop.READ
        )
    except socket.error as e:
        c = errno_from_exception(e)
        if c in _ERRNO_WOULDBLOCK:
            ioloop.add_handler(
                sock.fileno(),
                on_event,
                IOLoop.WRITE
            )
        else:
            sock.close()
            future.exception(e)
    # Add timeout handler
    ioloop.call_later(
        timeout,
        on_timeout
    )
    return future
