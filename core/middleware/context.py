# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Django template context
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import ujson
# NOC modules
from noc.core.cache.base import cache

CACHE_VERSION = 1


def messages(request):
    if "noc_user" in request.COOKIES:
        session_id = request.COOKIES["noc_user"].rsplit("|", 1)[-1]
        key = "msg-%s" % session_id
        msg = cache.get(key, version=CACHE_VERSION)
        if msg:
            messages = ujson.loads(msg)
            cache.delete(key, version=CACHE_VERSION)
            return {
                "messages": messages
            }
    return {}
