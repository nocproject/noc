# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Proxy settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
        aa = a.split("://", 1)[1]
        if aa.endswith("/"):
            aa = aa[:-1]
        host, port = aa.split(":")
        return host, int(port)

    if config.proxy.http_proxy:
        SYSTEM_PROXIES["http"] = get_addr(config.proxy.http_proxy)
    if config.proxy.https_proxy:
        SYSTEM_PROXIES["https"] = get_addr(config.proxy.https_proxy)
    if config.proxy.ftp_proxy:
        SYSTEM_PROXIES["ftp"] = get_addr(config.proxy.https_proxy)
    if not SYSTEM_PROXIES:
        logger.debug("No proxy servers configures")
    else:
        logger.debug("Using proxy servers: %s",
                     ", ".join("%s = %s" % (
                         k, SYSTEM_PROXIES[k]
                     ) for k in sorted(SYSTEM_PROXIES)))

_urllib_proxies_installed = False


def setup_urllib_proxies():
    import urllib2
    global _urllib_proxies_installed, SYSTEM_PROXIES

    if _urllib_proxies_installed:
        return
    else:
        _urllib_proxies_installed = True
    proxies = dict(
        (k, "%s://%s:%s" % (k, SYSTEM_PROXIES[k][0], SYSTEM_PROXIES[k][1]))
        for k in SYSTEM_PROXIES)
    if proxies:
        ph = urllib2.ProxyHandler(proxies)
        opener = urllib2.build_opener(ph)
        urllib2.install_opener(opener)


setup_proxies()
