#!./bin/python
# ----------------------------------------------------------------------
# NSQ Publish API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import orjson
from typing import Optional, Dict

# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_text
from noc.core.liftbridge.base import LiftBridgeClient
from noc.core.ioloop.util import run_sync

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


def publish(
    value: bytes,
    stream: str,
    partition: Optional[int] = None,
    key: Optional[bytes] = None,
    headers: Optional[Dict[str, bytes]] = None,
):
    async def wrap():
        async with LiftBridgeClient() as client:
            await client.publish(
                value=value, stream=stream, partition=partition, key=key, headers=headers
            )

    run_sync(wrap)
