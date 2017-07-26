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

NSQD_URL = "http://%s:%s/" % (config.nsqd.http_addresses[0].host, config.nsqd.http_addresses[0].port)
NSQD_PUB_URL = NSQD_URL + "pub"
NSQD_MPUB_URL = NSQD_URL + "mpub"

NSQD_CONNECT_TIMEOUT = config.nsqd.connect_timeout
NSQD_REQUEST_TIMEOUT = config.nsqd.request_timeout


def pub(topic, data):
    logger.debug("Publish to topic %s", topic)
    code, headers, body = fetch_sync(
            "%s?topic=%s" % (NSQD_PUB_URL, topic),
            method="POST",
            body=ujson.dumps(data),
            connect_timeout=NSQD_CONNECT_TIMEOUT,
            request_timeout=NSQD_REQUEST_TIMEOUT
    )
    if code != 200:
        raise Exception("Cannot publish: %s %s" % (code, body))
