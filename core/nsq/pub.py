# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Simple HTTP client for NSQ pub/mpub
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import ujson
import six
# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config
from .error import NSQPubError


def nsq_pub(topic, message):
    """
    Publish message to NSQ topic

    :param topic: NSQ topic name
    :param message: Raw message (Converted to JSON if is not a string)
    :return:
    """
    if not isinstance(message, six.string_types):
        message = ujson.dumps(message)
    # Resolve NSQd or wait
    si = config.nsqd.http_addresses[0]
    # Post message
    code, _, body = fetch_sync(
        "http://%s:%s/pub?topic=%s" % (si.host, si.port, topic),
        method="POST",
        body=message
    )
    if code != 200:
        raise NSQPubError("NSQ Pub error: code=%s message=%s" % (code, body))
