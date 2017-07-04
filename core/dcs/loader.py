# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
#----------------------------------------------------------------------

# Python modules
from threading import Lock
import os
# NOC modules
from noc.core.handler import get_handler

DEFAULT_DCS = os.environ.get("NOC_DCS", "consul://consul/noc")

DCS_HANDLERS = {
    "consul": "noc.core.dcs.consuldcs.ConsulDCS"
}

_lock = Lock()
_instances = {}


def get_dcs_url(url=None):
    return url or DEFAULT_DCS


def get_dcs_class(url=None):
    url = get_dcs_url(url)
    scheme = url.split(":", 1)[0]
    if scheme not in DCS_HANDLERS:
        raise ValueError("Unknown DCS handler: %s" % scheme)
    handler = get_handler(DCS_HANDLERS[scheme])
    if not handler:
        raise ValueError("Cannot initialize DCS handler: %s", scheme)
    return handler


def get_dcs(url=None, ioloop=None):
    """
    Return initialized DCS instance
    :param url: 
    :return: 
    """
    url = get_dcs_url(url)
    with _lock:
        if url not in _instances:
            _instances[url] = get_dcs_class(url)(url, ioloop=ioloop)
        return _instances[url]
