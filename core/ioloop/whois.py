# ----------------------------------------------------------------------
# Whois client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from tornado.tcpclient import TCPClient
import tornado.gen
from tornado.ioloop import IOLoop

# NOC modules
from noc.core.validators import is_fqdn
from noc.core.comp import smart_bytes, smart_text

DEFAULT_WHOIS_SERVER = "whois.ripe.net"
DEFAULT_WHOIS_PORT = 43
DEFAULT_TIMEOUT = 60

logger = logging.getLogger(__name__)

FIELDS_MAP = {
    "domain name": "domain",
    "name server": "nserver",
    "creation date": "created",
    "registry expiry date": "paid-till",
}


def parse_response(data):
    """
    Parse whois response
    :param data:
    :return:
    """
    r = []
    for line in data.splitlines():
        line = line.strip()
        if line.startswith(">>>"):
            break
        k, v = line.split(":", 1)
        k = k.strip().lower()
        k = FIELDS_MAP.get(k, k)
        r += [(k, v.strip())]
    return r


@tornado.gen.coroutine
def whois_async(query, fields=None):
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
        client = TCPClient()
        stream = yield client.connect(server, DEFAULT_WHOIS_PORT)
    except IOError as e:
        logger.error("Cannot resolve host '%s': %s", server, e)
        return
    try:
        yield stream.write(smart_bytes(query) + b"\r\n")
        data = yield stream.read_until_close()
    finally:
        yield stream.close()
    data = smart_text(data)
    data = parse_response(data)
    if fields:
        data = [(k, v) for k, v in data if k in fields]
    return data


def whois(query, fields=None):
    @tornado.gen.coroutine
    def _whois():
        result = yield whois_async(query, fields)
        r.append(result)

    r = []
    IOLoop().run_sync(_whois)
    return r[0]
