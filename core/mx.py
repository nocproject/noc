# ----------------------------------------------------------------------
# mx utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Dict
from threading import Lock

# Third-party modules
import orjson

# NOC services
from noc.core.service.loader import get_service
from noc.core.comp import smart_bytes
from noc.core.liftbridge.base import LiftBridgeClient
from noc.core.ioloop.util import run_sync

# MX stream name
MX_STREAM = "message"
# Headers
MX_MESSAGE_TYPE = "Message-Type"
MX_SHARDING_KEY = "Sharding-Key"
MX_TO = "To"
MX_CHANGE_ID = "Change-Id"
MX_ADMINISTRATIVE_DOMAIN_ID = "Administrative-Domain-Id"
MX_PROFILE_ID = "Profile-Id"
MX_LABELS = "Labels"
MX_H_VALUE_SPLITTER = ";"
# Available message types
MESSAGE_TYPES = {"alarm", "managedobject", "reboot", "metrics", "notification", "snmptrap"}
MESSAGE_HEADERS = {
    MX_SHARDING_KEY,
    MX_TO,
    MX_CHANGE_ID,
    MX_ADMINISTRATIVE_DOMAIN_ID,
    MX_PROFILE_ID,
    MX_LABELS,
}

_mx_partitions: Optional[int] = None
_mx_lock = Lock()


def send_message(
    data: Any,
    message_type: str,
    headers: Optional[Dict[str, bytes]],
    sharding_key: int = 0,
):
    """
    Build message and schedule to send to mx service

    :param data:
    :param message_type:
    :param headers:
    :param sharding_key:
    :return:
    """
    msg_headers = {
        MX_MESSAGE_TYPE: smart_bytes(message_type),
        MX_SHARDING_KEY: smart_bytes(sharding_key),
    }
    if headers:
        msg_headers.update(headers)
    svc = get_service()
    n_partitions = get_mx_partitions()
    svc.publish(
        value=orjson.dumps(data),
        stream=MX_STREAM,
        partition=sharding_key % n_partitions,
        headers=msg_headers,
    )


def get_mx_partitions() -> int:
    """
    Get number of MX stream partitions
    :return:
    """

    async def wrap():
        async with LiftBridgeClient() as client:
            r = await client.fetch_metadata(MX_STREAM, wait_for_stream=True)
            for m in r.metadata:
                if m.name == MX_STREAM:
                    return len(m.partitions)

    global _mx_partitions

    if _mx_partitions:
        return _mx_partitions
    with _mx_lock:
        if _mx_partitions:
            return _mx_partitions  # Set by concurrent thread
        _mx_partitions = run_sync(wrap)
        return _mx_partitions
