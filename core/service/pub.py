#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSQ Publish API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
# Third-party modules
import ujson
# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config

logger = logging.getLogger(__name__)


def pub(topic, data):
    logger.debug("Publish to topic %s", topic)
    url = "http://%s:%s/pub" % (config.nsqd.http_addresses[0].host,
                             config.nsqd.http_addresses[0].port)
    code, headers, body = fetch_sync(
            "%s?topic=%s" % (url, topic),
            method="POST",
            body=ujson.dumps(data),
            connect_timeout=config.nsqd.connect_timeout,
            request_timeout=config.nsqd.request_timeout
    )
    if code != 200:
        raise Exception("Cannot publish: %s %s" % (code, body))
