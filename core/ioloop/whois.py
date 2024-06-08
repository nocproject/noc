# ----------------------------------------------------------------------
# Whois client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import asyncio
import socket

# NOC modules
from noc.core.validators import is_fqdn
from noc.core.comp import smart_bytes, smart_text
from noc.core.ioloop.util import run_sync

DEFAULT_WHOIS_SERVER = "whois.ripe.net"
DEFAULT_WHOIS_PORT = 43

logger = logging.getLogger(__name__)

FIELDS_MAP = {
    "domain name": "domain",
    "name server": "nserver",
    "creation date": "created",
    "registry expiry date": "paid-till",
}


def parse_response(data):
    """Parse whois response

    :param data:
    :return:
    """
    r = []
    for line in data.splitlines():
        line = line.strip()
        if line.startswith(">>>"):
            break
        if not line.startswith("%") and ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().lower()
            k = FIELDS_MAP.get(k, k)
            r += [(k, v.strip())]
    return r


async def send_whois_request(host: str, port: int, query: bytes) -> bytes:
    """Sending a TCP request to the whois server

    :param host: Whois server
    :param port: Port
    :param query: Domain name to search
    :return: Query result
    """
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(query)
    await writer.drain()
    response = b""
    while True:
        data = await reader.read(3072)
        if not data:
            break
        response += data
    writer.close()
    await writer.wait_closed()
    return response


async def whois_async(query, fields=None):
    """
    Perform whois request
    :param query:
    :param fields:
    :return:
    """
    logger.debug("whois %s", query)
    # Get appropriate whois server
    if is_fqdn(query):
        # Use TLD.whois-servers.net for domain lookup
        tld = query.split(".")[-1]
        server = "%s.whois-servers.net" % tld
    else:
        server = DEFAULT_WHOIS_SERVER
    # Perform query
    try:
        query = smart_bytes(query) + b"\r\n"
        data = await send_whois_request(host=server, port=DEFAULT_WHOIS_PORT, query=query)
    except socket.gaierror as e:
        logger.error(f"Cannot resolve host {server}: {e}")
        return
    data = smart_text(data)
    data = parse_response(data)
    if fields:
        data = [(k, v) for k, v in data if k in fields]
    return data


def whois(query, fields=None):
    async def _whois():
        return await whois_async(query, fields)

    return run_sync(_whois)
