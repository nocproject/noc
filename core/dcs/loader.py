# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base service
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import os
## NOC modules
from noc.core.handler import get_handler

DEFAULT_DCS = os.environ.get("NOC_DCS", "consul://consul/noc")

DCS_HANDLERS = {
    "consul": "noc.core.dcs.consuldcs.ConsulDCS"
}

_lock = Lock()
_instances = {}


def get_dcs(url=None):
    """
    Return initialized DCS instance
    :param url: 
    :return: 
    """
    with _lock:
        if url not in _instances:
            scheme = url.split(":", 1)[0]
            if scheme not in DCS_HANDLERS:
                raise ValueError("Unknown DCS handler: %s" % scheme)
            handler = get_handler(DCS_HANDLERS[scheme])
            if not handler:
                raise ValueError("Cannot initialize DCS handler: %s", scheme)
            _instances[url] = handler(url)
        return _instances[url]
