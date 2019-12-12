# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Proxy settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.config import config

logger = logging.getLogger(__name__)

SYSTEM_PROXIES = {}


def setup_proxies():
    def get_addr(a):
        if "://" in a:
            aa = a.split("://", 1)[1]
            if aa.endswith("/"):
                aa = aa[:-1]
            host, port = aa.rsplit(":", 1)
        else:
            host, port = a.rsplit(":", 1)
        return host, int(port)

    if config.proxy.http_proxy:
        SYSTEM_PROXIES["http"] = get_addr(config.proxy.http_proxy)
    if config.proxy.https_proxy:
        SYSTEM_PROXIES["https"] = get_addr(config.proxy.https_proxy)
    if config.proxy.ftp_proxy:
        SYSTEM_PROXIES["ftp"] = get_addr(config.proxy.https_proxy)
    if not SYSTEM_PROXIES:
        logger.debug("No proxy servers configured")
    else:
        logger.debug(
            "Using proxy servers: %s",
            ", ".join("%s = %s" % (k, SYSTEM_PROXIES[k]) for k in sorted(SYSTEM_PROXIES)),
        )


_urllib_proxies_installed = False


def setup_urllib_proxies():
    global _urllib_proxies_installed, SYSTEM_PROXIES

    if _urllib_proxies_installed:
        return
    _urllib_proxies_installed = True
    if not SYSTEM_PROXIES:
        return
    proxies = dict(
        (k, "%s://%s:%s" % (k, SYSTEM_PROXIES[k][0], SYSTEM_PROXIES[k][1])) for k in SYSTEM_PROXIES
    )
    from six.moves.urllib.request import ProxyHandler, build_opener, install_opener

    proxy_handler = ProxyHandler(proxies)
    opener = build_opener(proxy_handler)
    install_opener(opener)


setup_proxies()
