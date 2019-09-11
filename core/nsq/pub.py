# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Simple HTTP client for NSQ pub/mpub
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import struct

# Third-party modules
import ujson
import six
import tornado.gen

# NOC modules
from noc.core.http.client import fetch_sync, fetch
from noc.core.dcs.loader import get_dcs
from noc.config import config
from noc.core.perf import metrics
from .error import NSQPubError

NSQ_HTTP_SERVICE = "nsqdhttp"
logger = logging.getLogger(__name__)


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
        "http://%s:%s/pub?topic=%s" % (si.host, si.port, topic), method="POST", body=message
    )
    if code != 200:
        raise NSQPubError("NSQ Pub error: code=%s message=%s" % (code, body))


def mpub_encode(messages):
    """
    Build mpub binary message
    :param messages: List of messages
    :return: Serialized message body
    """

    def iter_msg():
        # Amount of messages in pack
        yield struct.pack("!i", len(messages))
        for msg in messages:
            if not isinstance(msg, six.string_types):
                msg = ujson.dumps(msg)
            yield struct.pack("!i", len(msg))
            yield msg

    if not messages:
        return ""
    return "".join(iter_msg())


@tornado.gen.coroutine
def mpub(topic, messages, dcs=None, io_loop=None, retries=None):
    """
    Asynchronously publish message to NSQ topic

    :param topic: NSQ topic
    :param messages: List of strings containing messages
    :param dcs: DSC instance
    :param io_loop: IOLoop instance
    :param retries: Error retries. config.nsqd.pub_retries by default
    :return: None
    :raises NSQPubError: On publish error
    """
    if not messages:
        raise tornado.gen.Return()
    if not dcs:
        # No global DCS, instantiate one
        dcs = get_dcs(ioloop=io_loop)
    # Build body
    msg = mpub_encode(messages)
    # Post message
    retries = retries or config.nsqd.pub_retries
    code = 200
    body = None
    metrics["nsq_mpub", ("topic", topic)] += 1
    while retries > 0:
        # Get actual nsqd service's address and port
        si = yield dcs.resolve(NSQ_HTTP_SERVICE, near=True)
        # Send message
        code, _, body = yield fetch(
            "http://%s/mpub?topic=%s&binary=true" % (si, topic),
            method="POST",
            body=msg,
            io_loop=io_loop,
            connect_timeout=config.nsqd.connect_timeout,
            request_timeout=config.nsqd.request_timeout,
        )
        if code == 200:
            break
        metrics["nsq_mpub_error", ("topic", topic)] += 1
        logger.error("Failed to pub to topic '%s': %s (Code=%d)", topic, body, code)
        retries -= 1
        if retries > 0:
            yield tornado.gen.sleep(config.nsqd.pub_retry_delay)
    if code != 200:
        logger.error("Failed to pub to topic '%s'. Giving up", topic)
        metrics["nsq_mpub_fail", ("topic", topic)] += 1
        raise NSQPubError("NSQ Pub error: code=%s message=%s" % (code, body))
