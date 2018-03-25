# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SNMP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import socket
import errno
# Third-party modules
from tornado.gen import coroutine, Return
import six
# NOC modules
from noc.core.snmp.version import SNMP_v2c
from noc.core.snmp.get import (get_pdu, getnext_pdu, getbulk_pdu,
                               parse_get_response)
from noc.core.snmp.set import set_pdu
from noc.core.snmp.error import (NO_ERROR, NO_SUCH_NAME,
                                 SNMPError, TIMED_OUT, UNREACHABLE)
from noc.core.ioloop.udp import UDPSocket

_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)
logger = logging.getLogger(__name__)
BULK_MAX_REPETITIONS = 20


@coroutine
def snmp_get(address, oids, port=161,
             community="public",
             version=SNMP_v2c,
             timeout=10,
             tos=None,
             ioloop=None,
             udp_socket=None):
    """
    Perform SNMP get request and returns Future to be used
    inside @tornado.gen.coroutine
    """
    oid_map = {}
    if isinstance(oids, six.string_types):
        oids = [oids]
    elif isinstance(oids, dict):
        oid_map = dict((oids[k], k) for k in oids)
        oids = oids.values()
    else:
        raise ValueError("oids must be either string or dict")
    logger.debug("[%s] SNMP GET %s", address, oids)
    # Send GET PDU
    pdu = get_pdu(community=community, oids=oids, version=version)
    if udp_socket:
        sock = udp_socket
        prev_timeout = sock.get_timeout()
    else:
        sock = UDPSocket(ioloop=ioloop, tos=tos)
    sock.settimeout(timeout)
    # Wait for result
    try:
        yield sock.sendto(pdu, (address, port))
        data, addr = yield sock.recvfrom(4096)
    except socket.timeout:
        raise SNMPError(code=TIMED_OUT, oid=oids[0])
    except socket.gaierror as e:
        logger.debug("[%s] Cannot resolve address: %s", address, e)
        raise SNMPError(code=UNREACHABLE, oid=oids[0])
    except socket.error as e:
        logger.debug("[%s] Socket error: %s", address, e)
        raise SNMPError(code=UNREACHABLE, oid=oids[0])
    finally:
        if udp_socket:
            sock.settimeout(prev_timeout)
        else:
            sock.close()
    resp = parse_get_response(data)
    if resp.error_status == NO_ERROR:
        # Success
        if oid_map:
            result = {}
            for k, v in resp.varbinds:
                if k in oid_map:
                    result[oid_map[k]] = v
                else:
                    logger.error(
                        "[%s] Invalid oid %s returned in reply",
                        address, k
                    )
        else:
            result = resp.varbinds[0][1]
        logger.debug("[%s] GET result: %r", address, result)
        raise Return(result)
    elif resp.error_status == NO_SUCH_NAME and len(oids) > 1:
        # One or more invalid oids
        b_idx = resp.error_index - 1
        logger.debug("[%s] Invalid oid %s detected, trying to exclude",
                     address, resp.varbinds[b_idx][0])
        result = {}
        oid_parts = []
        if b_idx:
            # Oids before b_idx are probable correct
            oid_parts += [[vb[0] for vb in resp.varbinds[:b_idx]]]
        if b_idx < len(resp.varbinds) - 1:
            # Some oids after b_idx may be correct
            oid_parts += [[vb[0] for vb in resp.varbinds[b_idx + 1:]]]
        for new_oids in oid_parts:
            try:
                new_result = yield snmp_get(
                    address=address,
                    oids=dict((k, k) for k in new_oids),
                    port=port,
                    community=community,
                    version=version,
                    timeout=timeout,
                    tos=tos,
                    ioloop=ioloop,
                    udp_socket=sock
                )
            except SNMPError as e:
                if e.code == NO_SUCH_NAME and len(new_oids) == 1:
                    # Ignore NO_SUCH_VALUE for last oid in list
                    new_result = {}
                else:
                    raise
            for k in new_result:
                if k in oid_map:
                    result[oid_map[k]] = new_result[k]
                else:
                    logger.info(
                        "[%s] Invalid oid %s returned in reply",
                        address, k
                    )
        if result:
            logger.debug("[%s] GET result: %r", address, result)
            raise Return(result)
        else:
            # All oids excluded as broken
            logger.debug("[%s] All oids are broken", address)
            raise SNMPError(code=NO_SUCH_NAME, oid=oids[0])
    else:
        oid = None
        if resp.error_index and resp.varbinds:
            oid = resp.varbinds[resp.error_index - 1][0]
        logger.debug("[%s] SNMP error: %s %s",
                     address, oid, resp.error_status)
        raise SNMPError(code=resp.error_status, oid=oid)


@coroutine
def snmp_count(address, oid, port=161,
               community="public",
               version=SNMP_v2c,
               timeout=10,
               bulk=False,
               filter=None,
               max_repetitions=BULK_MAX_REPETITIONS,
               tos=None,
               ioloop=None,
               udp_socket=None):
    """
    Perform SNMP get request and returns Future to be used
    inside @tornado.gen.coroutine
    """
    def true(x, y):
        return true

    logger.debug("[%s] SNMP COUNT %s", address, oid)
    if not filter:
        filter = true
    poid = oid + "."
    result = 0
    if udp_socket:
        sock = udp_socket
        prev_timeout = sock.get_timeout()
    else:
        sock = UDPSocket(ioloop=ioloop, tos=tos)
    sock.settimeout(timeout)
    while True:
        # Get PDU
        if bulk:
            pdu = getbulk_pdu(community, oid,
                              max_repetitions=max_repetitions,
                              version=version)
        else:
            pdu = getnext_pdu(community, oid, version=version)
        # Send request and wait for response
        try:
            yield sock.sendto(pdu, (address, port))
            data, addr = yield sock.recvfrom(4096)
        except socket.timeout:
            raise SNMPError(code=TIMED_OUT, oid=oid)
        except socket.gaierror as e:
            logger.debug("[%s] Cannot resolve address: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=oid)
        except socket.error as e:
            logger.debug("[%s] Socket error: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=oid)
        finally:
            if udp_socket:
                sock.settimeout(prev_timeout)
            else:
                sock.close()
        # Parse response
        resp = parse_get_response(data)
        if resp.error_status == NO_SUCH_NAME:
            # NULL result
            break
        elif resp.error_status != NO_ERROR:
            # Error
            raise SNMPError(code=resp.error_status, oid=oid)
        else:
            # Success value
            for oid, v in resp.varbinds:
                if oid.startswith(poid):
                    # Next value
                    if filter(oid, v):
                        result += 1
                else:
                    logger.debug("[%s] COUNT result: %s",
                                 address, result)
                    sock.close()
                    raise Return(result)


@coroutine
def snmp_getnext(address, oid, port=161,
                 community="public",
                 version=SNMP_v2c,
                 timeout=10,
                 bulk=False,
                 filter=None,
                 max_repetitions=BULK_MAX_REPETITIONS,
                 only_first=False,
                 tos=None,
                 ioloop=None,
                 udp_socket=None,
                 max_retries=0):
    """
    Perform SNMP GETNEXT/BULK request and returns Future to be used
    inside @tornado.gen.coroutine
    """
    def true(x, y):
        return True

    def close_socket():
        if udp_socket:
            sock.settimeout(prev_timeout)
        else:
            sock.close()

    logger.debug("[%s] SNMP GETNEXT %s", address, oid)
    if not filter:
        filter = true
    poid = oid + "."
    result = []
    if udp_socket:
        sock = udp_socket
        prev_timeout = sock.get_timeout()
    else:
        sock = UDPSocket(ioloop=ioloop, tos=tos)
    sock.settimeout(timeout)
    while True:
        # Get PDU
        if bulk:
            pdu = getbulk_pdu(
                community, oid,
                max_repetitions=max_repetitions or BULK_MAX_REPETITIONS,
                version=version
            )
        else:
            pdu = getnext_pdu(community, oid, version=version)
        # Send request and wait for response
        try:
            yield sock.sendto(pdu, (address, port))
            data, addr = yield sock.recvfrom(4096)
        except socket.timeout:
            if not max_retries:
                close_socket()
                raise SNMPError(code=TIMED_OUT, oid=oid)
            max_retries -= 1
            continue
        except socket.gaierror as e:
            logger.debug("[%s] Cannot resolve address: %s", address, e)
            close_socket()
            raise SNMPError(code=UNREACHABLE, oid=oid)
        except socket.error as e:
            logger.debug("[%s] Socket error: %s", address, e)
            close_socket()
            raise SNMPError(code=UNREACHABLE, oid=oid)
        # Parse response
        resp = parse_get_response(data)
        if resp.error_status == NO_SUCH_NAME:
            # NULL result
            break
        elif resp.error_status != NO_ERROR:
            # Error
            close_socket()
            raise SNMPError(code=resp.error_status, oid=oid)
        else:
            # Success value
            for oid, v in resp.varbinds:
                if oid.startswith(poid) and not (only_first and result):
                    # Next value
                    if filter(oid, v):
                        result += [(oid, v)]
                else:
                    logger.debug("[%s] GETNEXT result: %s",
                                 address, result)
                    close_socket()
                    raise Return(result)
    close_socket()


@coroutine
def snmp_set(address, varbinds, port=161,
             community="public",
             version=SNMP_v2c,
             timeout=10,
             tos=None,
             ioloop=None,
             udp_socket=None):
    """
    Perform SNMP set request and returns Future to be used
    inside @tornado.gen.coroutine
    """
    logger.debug("[%s] SNMP SET %s", address, varbinds)
    if udp_socket:
        sock = udp_socket
        prev_timeout = sock.get_timeout()  # noqa
    else:
        sock = UDPSocket(ioloop=ioloop, tos=tos)
    sock.settimeout(timeout)
    # Send GET PDU
    pdu = set_pdu(community=community, varbinds=varbinds, version=version)
    # Wait for result
    try:
        yield sock.sendto(pdu, (address, port))
        data, addr = yield sock.recvfrom(4096)
    except socket.timeout:
        raise SNMPError(code=TIMED_OUT, oid=varbinds[0][0])
    except socket.gaierror as e:
        logger.debug("[%s] Cannot resolve address: %s", address, e)
        raise SNMPError(code=UNREACHABLE, oid=varbinds[0][0])
    except socket.error as e:
        logger.debug("[%s] Socket error: %s", address, e)
        raise SNMPError(code=UNREACHABLE, oid=varbinds[0][0])
    finally:
        if udp_socket:
            sock.settimeout(None)
        else:
            sock.close()
    resp = parse_get_response(data)
    if resp.error_status != NO_ERROR:
        oid = None
        if resp.error_index and resp.varbinds:
            oid = resp.varbinds[resp.error_index - 1][0]
        logger.debug("[%s] SNMP error: %s %s",
                     address, oid, resp.error_status)
        raise SNMPError(code=resp.error_status, oid=oid)
    else:
        logger.debug("[%s] SET result: OK", address)
        raise Return(True)
