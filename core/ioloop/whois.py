# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Whois client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from tornado.tcpclient import TCPClient
import tornado.gen
import tornado.ioloop

# NOC modules
from noc.core.validators import is_fqdn

DEFAULT_WHOIS_SERVER = "whois.ripe.net"
DEFAULT_WHOIS_PORT = 43
DEFAULT_TIMEOUT = 60

logger = logging.getLogger(__name__)

VERISIGN_MAP = {
    "domain name": "domain",
    "name server": "nserver",
    "creation date": "created",
    "registry expiry date": "paid-till",
}


def parse_verisign(data):
    """
    Parse whois response from verisign
    :param data:
    :return:
    """
    r = []
    for line in data.splitlines():
        if not line.startswith("  "):
            continue
        line = line.strip()
        k, v = line.split(":", 1)
        k = k.strip().lower()
        k = VERISIGN_MAP.get(k, k)
        r += [(k, v.strip())]
    return r


def parse_response(data):
    """
    Parse whois response
    :param data:
    :return:
    """
    if data.startswith(" ") and ">>> Last update of whois database" in data:
        return parse_verisign(data)


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
        raise tornado.gen.Return()
    try:
        yield stream.write(str(query) + "\r\n")
        data = yield stream.read_until_close()
    finally:
        yield stream.close()
    data = parse_response(data)
    if fields:
        data = [(k, v) for k, v in data if k in fields]
    raise tornado.gen.Return(data)


def whois(query, fields=None):
    @tornado.gen.coroutine
    def _whois():
        result = yield whois_async(query, fields)
        r.append(result)

    ioloop = tornado.ioloop.IOLoop.instance()
    r = []
    ioloop.run_sync(_whois)
    return r[0]
