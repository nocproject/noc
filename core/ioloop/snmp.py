# ----------------------------------------------------------------------
# SNMP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import socket
import errno
import asyncio
from typing import Optional, Callable, Any, Dict, Union

# NOC modules
from noc.core.snmp.version import SNMP_v2c
from noc.core.snmp.get import (
    get_pdu,
    getnext_pdu,
    getbulk_pdu,
    _ResponseParser,
    parse_get_response,
    parse_get_response_raw,
)
from noc.core.snmp.set import set_pdu
from noc.core.snmp.error import (
    NO_ERROR,
    NO_SUCH_NAME,
    SNMPError,
    TIMED_OUT,
    UNREACHABLE,
    BER_ERROR,
    END_OID_TREE,
    BAD_VALUE,
)
from noc.core.ioloop.udp import UDPSocket, UDPSocketContext
from noc.core.comp import smart_text
from noc.core.ratelimit.asyncio import AsyncRateLimit

_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)
logger = logging.getLogger(__name__)
BULK_MAX_REPETITIONS = 20


def _get_parser(
    parser: Optional[_ResponseParser] = None, raw_varbinds: bool = False
) -> _ResponseParser:
    if raw_varbinds:
        return parse_get_response_raw
    return parser or parse_get_response


async def snmp_get(
    address,
    oids,
    port=161,
    community="public",
    version=SNMP_v2c,
    timeout=10,
    tos=None,
    udp_socket: Optional[UDPSocket] = None,
    raw_varbinds=False,
    display_hints=None,
    response_parser: Optional[_ResponseParser] = None,
    rate_limit: Optional[AsyncRateLimit] = None,
):
    """
    Perform SNMP get request and returns Future to be used
    inside async coroutine
    """
    oid_map = {}
    if isinstance(oids, str):
        oids = [oids]
    elif isinstance(oids, dict):
        oid_map = {oids[k]: k for k in oids}
        oids = list(oids.values())
    else:
        raise ValueError("oids must be either string or dict")
    logger.debug("[%s] SNMP GET %s", address, oids)
    parser = _get_parser(response_parser, raw_varbinds)
    # Send GET PDU
    pdu = get_pdu(community=community, oids=oids, version=version)
    if rate_limit:
        await rate_limit.wait()
    with UDPSocketContext(udp_socket, tos=tos) as sock:
        try:
            data, addr = await asyncio.wait_for(
                sock.send_and_receive(pdu, (address, port)), timeout
            )
        except asyncio.TimeoutError:
            raise SNMPError(code=TIMED_OUT, oid=oids[0])
        except socket.gaierror as e:
            logger.debug("[%s] Cannot resolve address: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=oids[0])
        except OSError as e:
            logger.debug("[%s] Socket error: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=oids[0])
        try:
            resp = parser(data, display_hints)
        except ValueError:
            # Broken response
            raise SNMPError(code=BER_ERROR, oid=oids[0])
        if resp.error_status == NO_ERROR:
            # Success
            if oid_map:
                result = {}
                for k, v in resp.varbinds:
                    if k in oid_map:
                        result[oid_map[k]] = v
                    else:
                        logger.error("[%s] Invalid oid %s returned in reply", address, k)
            elif resp.varbinds:
                result = resp.varbinds[0][1]
            else:
                # Device return empty varbinds, perhaps need more info
                raise SNMPError(code=BAD_VALUE, oid=oids)
            logger.debug("[%s] GET result: %r", address, result)
            return result
        if resp.error_status == NO_SUCH_NAME and resp.varbinds and len(oids) > 1:
            # One or more invalid oids
            b_idx = resp.error_index - 1
            logger.debug(
                "[%s] Invalid oid %s detected, trying to exclude", address, resp.varbinds[b_idx][0]
            )
            result = {}
            oid_parts = []
            if b_idx:
                # Oids before b_idx are probable correct
                oid_parts += [[vb[0] for vb in resp.varbinds[:b_idx]]]
            if b_idx < len(resp.varbinds) - 1:
                # Some oids after b_idx may be correct
                oid_parts += [[vb[0] for vb in resp.varbinds[b_idx + 1 :]]]
            for new_oids in oid_parts:
                try:
                    new_result = await snmp_get(
                        address=address,
                        oids={k: k for k in new_oids},
                        port=port,
                        community=community,
                        version=version,
                        timeout=timeout,
                        tos=tos,
                        udp_socket=sock,
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
                        logger.info("[%s] Invalid oid %s returned in reply", address, k)
            if result:
                logger.debug("[%s] GET result: %r", address, result)
                return result
            # All oids excluded as broken
            logger.debug("[%s] All oids are broken", address)
            raise SNMPError(code=NO_SUCH_NAME, oid=oids[0])
        oid = None
        if resp.error_index and resp.varbinds:
            if resp.error_index & 0x8000:
                # Some broken SNMP servers (i.e. Huawei) returns
                # negative error index. Try to negotiate silently
                oid = resp.varbinds[min(65536 - resp.error_index, len(resp.varbinds) - 1)][0]
            else:
                oid = resp.varbinds[resp.error_index - 1][0]
        logger.debug("[%s] SNMP error: %s %s", address, oid, resp.error_status)
        raise SNMPError(code=resp.error_status, oid=oid)


async def snmp_count(
    address,
    oid,
    port=161,
    community="public",
    version=SNMP_v2c,
    timeout=10,
    bulk=False,
    filter=None,
    max_repetitions=BULK_MAX_REPETITIONS,
    tos=None,
    udp_socket: Optional[UDPSocket] = None,
    rate_limit: Optional[AsyncRateLimit] = None,
):
    """
    Perform SNMP get request and returns Future to be used
    inside async coroutine
    """

    def true(x, y):
        return true

    logger.debug("[%s] SNMP COUNT %s", address, oid)
    if not filter:
        filter = true
    poid = oid + "."
    result = 0
    with UDPSocketContext(udp_socket, tos=tos) as sock:
        while True:
            if rate_limit:
                await rate_limit.wait()
            # Get PDU
            if bulk:
                pdu = getbulk_pdu(community, oid, max_repetitions=max_repetitions, version=version)
            else:
                pdu = getnext_pdu(community, oid, version=version)
            # Send request and wait for response
            try:
                data, addr = await asyncio.wait_for(
                    sock.send_and_receive(pdu, (address, port)), timeout
                )
            except asyncio.TimeoutError:
                raise SNMPError(code=TIMED_OUT, oid=oid)
            except socket.gaierror as e:
                logger.debug("[%s] Cannot resolve address: %s", address, e)
                raise SNMPError(code=UNREACHABLE, oid=oid)
            except OSError as e:
                logger.debug("[%s] Socket error: %s", address, e)
                raise SNMPError(code=UNREACHABLE, oid=oid)
            # Parse response
            try:
                resp = parse_get_response(data)
            except ValueError:
                raise SNMPError(code=BER_ERROR, oid=oid)
            if resp.error_status == NO_SUCH_NAME:
                # NULL result
                break
            if resp.error_status != NO_ERROR:
                # Error
                raise SNMPError(code=resp.error_status, oid=oid)
            # Success value
            for oid, v in resp.varbinds:
                if oid.startswith(poid):
                    # Next value
                    if filter(oid, v):
                        result += 1
                else:
                    logger.debug("[%s] COUNT result: %s", address, result)
                    sock.close()
                    return result


async def snmp_getnext(
    address: str,
    oid: str,
    port: int = 161,
    community: str = "public",
    version: int = SNMP_v2c,
    timeout: float = 10,
    bulk: bool = False,
    filter: Optional[Callable[[bytes, Any], bool]] = None,
    max_repetitions: int = BULK_MAX_REPETITIONS,
    only_first: bool = False,
    tos: Optional[int] = None,
    udp_socket: Optional[UDPSocket] = None,
    max_retries: int = 0,
    raw_varbinds: bool = False,
    display_hints: Optional[Dict[str, Optional[Callable[[str, bytes], Union[str, bytes]]]]] = None,
    response_parser: Optional[_ResponseParser] = None,
    rate_limit: Optional[AsyncRateLimit] = None,
):
    """
    Perform SNMP GETNEXT/BULK request and returns Future to be used
    inside async coroutine
    """

    def true(x, y):
        return True

    logger.debug("[%s] SNMP GETNEXT %s", address, oid)
    if not filter:
        filter = true
    poid = oid + "."
    result = []
    parser = _get_parser(response_parser, raw_varbinds)
    with UDPSocketContext(udp_socket, tos=tos) as sock:
        first_oid = None
        last_oid = None
        while True:
            if rate_limit:
                await rate_limit.wait()
            # Get PDU
            if bulk:
                pdu = getbulk_pdu(
                    community,
                    oid,
                    max_repetitions=max_repetitions or BULK_MAX_REPETITIONS,
                    version=version,
                )
            else:
                pdu = getnext_pdu(community, oid, version=version)
            # Send request and wait for response
            try:
                data, addr = await asyncio.wait_for(
                    sock.send_and_receive(pdu, (address, port)), timeout
                )
            except asyncio.TimeoutError:
                if not max_retries:
                    raise SNMPError(code=TIMED_OUT, oid=oid)
                max_retries -= 1
                continue
            except socket.gaierror as e:
                logger.debug("[%s] Cannot resolve address: %s", address, e)
                raise SNMPError(code=UNREACHABLE, oid=oid)
            except OSError as e:
                logger.debug("[%s] Socket error: %s", address, e)
                raise SNMPError(code=UNREACHABLE, oid=oid)
            # Parse response
            try:
                resp = parser(data, display_hints)
            except ValueError:
                raise SNMPError(code=BER_ERROR, oid=oid)
            if resp.error_status == NO_SUCH_NAME:
                # NULL result
                break
            if resp.error_status == END_OID_TREE:
                # End OID Tree
                return result
            if resp.error_status != NO_ERROR:
                # Error
                raise SNMPError(code=resp.error_status, oid=oid)
            if not raw_varbinds:
                # Success value
                for oid, v in resp.varbinds:
                    if oid == first_oid:
                        logger.warning("[%s] GETNEXT Oid wrap detected", address)
                        return result
                    if oid.startswith(poid) and not (only_first and result) and oid != last_oid:
                        # Next value
                        if filter(oid, v):
                            result += [(oid, v)]
                        last_oid = oid
                        first_oid = first_oid or oid
                    else:
                        logger.debug("[%s] GETNEXT result: %s", address, result)
                        return result
            else:
                # Raw varbinds
                for oid, v in resp.varbinds:
                    s_oid = smart_text(oid)
                    if s_oid.startswith(poid) and not (only_first and result) and oid != last_oid:
                        # Next value
                        if filter(s_oid, v):
                            result += [(oid, v)]
                        last_oid = oid
                        first_oid = first_oid or oid
                    else:
                        logger.debug("[%s] GETNEXT result: %s", address, result)
                        return result


async def snmp_set(
    address,
    varbinds,
    port=161,
    community="public",
    version=SNMP_v2c,
    timeout=10,
    tos=None,
    udp_socket=None,
    rate_limit: Optional[AsyncRateLimit] = None,
):
    """
    Perform SNMP set request and returns Future to be used
    inside async coroutine
    """
    logger.debug("[%s] SNMP SET %s", address, varbinds)
    # Send GET PDU
    pdu = set_pdu(community=community, varbinds=varbinds, version=version)
    if rate_limit:
        await rate_limit.wait()
    # Wait for result
    with UDPSocketContext(udp_socket, tos=tos) as sock:
        try:
            data, addr = await asyncio.wait_for(
                sock.send_and_receive(pdu, (address, port)), timeout
            )
        except asyncio.TimeoutError:
            raise SNMPError(code=TIMED_OUT, oid=varbinds[0][0])
        except socket.gaierror as e:
            logger.debug("[%s] Cannot resolve address: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=varbinds[0][0])
        except OSError as e:
            logger.debug("[%s] Socket error: %s", address, e)
            raise SNMPError(code=UNREACHABLE, oid=varbinds[0][0])
        try:
            resp = parse_get_response(data)
        except ValueError:
            raise SNMPError(code=BER_ERROR, oid=varbinds[0][0])
        if resp.error_status != NO_ERROR:
            oid = None
            if resp.error_index and resp.varbinds:
                oid = resp.varbinds[resp.error_index - 1][0]
            logger.debug("[%s] SNMP error: %s %s", address, oid, resp.error_status)
            raise SNMPError(code=resp.error_status, oid=oid)
        logger.debug("[%s] SET result: OK", address)
        return True
