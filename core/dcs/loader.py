# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from noc.core.handler import get_handler


DCS_HANDLERS = {
    "consul": "noc.core.dcs.consuldcs.ConsulDCS"
}


def get_dcs(url):
    scheme = url.split(":", 1)[0]
    if scheme not in DCS_HANDLERS:
        raise ValueError("Unknown DCS handler: %s" % scheme)
    handler = get_handler(DCS_HANDLERS[scheme])
    if not handler:
        raise ValueError("Cannot initialize DCS handler: %s", scheme)
    return handler(url)
