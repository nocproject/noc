#!./bin/python
# ----------------------------------------------------------------------
# NSQ Publish API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import orjson

# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


def pub(topic, data, raw=False):
    logger.debug("Publish to topic %s", topic)
    url = "http://%s:%s/pub" % (
        config.nsqd.http_addresses[0].host,
        config.nsqd.http_addresses[0].port,
    )
    code, headers, body = fetch_sync(
        "%s?topic=%s" % (url, topic),
        method="POST",
        body=data if raw else smart_text(orjson.dumps(data)),
        connect_timeout=config.nsqd.connect_timeout,
        request_timeout=config.nsqd.request_timeout,
    )
    if code != 200:
        metrics["error", ("type", "nsq_pub_error_code %s" % code)] += 1
        raise Exception("Cannot publish: %s %s" % (code, body))
