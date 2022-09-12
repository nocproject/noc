#!./bin/python
# ----------------------------------------------------------------------
# Liftbridge Publish API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from typing import Optional, Dict

# NOC modules
from noc.core.messagestream.base import stream_client
from noc.core.ioloop.util import run_sync

logger = logging.getLogger(__name__)


def publish(
    value: bytes,
    stream: str,
    partition: Optional[int] = None,
    key: Optional[bytes] = None,
    headers: Optional[Dict[str, bytes]] = None,
):
    async def wrap():
        async with stream_client() as client:
            await client.publish(
                value=value, stream=stream, partition=partition, key=key, headers=headers
            )

    run_sync(wrap)
