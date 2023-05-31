# ----------------------------------------------------------------------
# mx utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, Dict
from threading import Lock
from dataclasses import dataclass
from functools import partial

# NOC services
from noc.core.service.loader import get_service
from noc.core.comp import DEFAULT_ENCODING
from noc.core.ioloop.util import run_sync


@dataclass
class Message(object):
    value: bytes
    headers: Dict[str, bytes]
    timestamp: int
    key: int


# MX stream name
MX_STREAM = "message"
MX_METRICS_TYPE = "metrics"
MX_METRICS_SCOPE = "Metric-Scope"
#
MX_SPAN_CTX = "NOC-Span-Ctx"
MX_SPAN_ID = "Span-Id"
# Headers
MX_MESSAGE_TYPE = "Message-Type"
MX_SHARDING_KEY = "Sharding-Key"
MX_CHANGE_ID = "Change-Id"
MX_DATA_ID = "Data-Id"
MX_ADMINISTRATIVE_DOMAIN_ID = "Administrative-Domain-Id"
MX_PROFILE_ID = "Profile-Id"
MX_LABELS = "Labels"
MX_TO = "To"
MX_NOTIFICATION = "notification"
MX_NOTIFICATION_CHANNEL = "Notification-Channel"
MX_LANG = "Language"
KAFKA_PARTITION = "Kafka-Partition"
#
MX_H_VALUE_SPLITTER = ";"
# Available message types
MESSAGE_TYPES = {
    "alarm",
    "managedobject",
    "reboot",
    "metrics",
    "snmptrap",
    "syslog",
    "event",
    "interface_status_change",
    "config_changed",
    "object_new",
    "object_deleted",
    "version_changed",
    "config_policy_violation",
}
MESSAGE_HEADERS = {
    MX_SHARDING_KEY,
    MX_CHANGE_ID,
    MX_ADMINISTRATIVE_DOMAIN_ID,
    MX_PROFILE_ID,
    MX_TO,
    MX_LANG,
    KAFKA_PARTITION,
    MX_METRICS_SCOPE,
}
# Method -> Sender stream map, ?autoregister
NOTIFICATION_METHODS = {"mail": "mailsender", "tg": "tgsender", "icq": "icqsender"}

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

    :param data: Data for transmit
    :param message_type: Message type
    :param headers: additional message headers
    :param sharding_key: Key for sharding over MX services
    :return:
    """
    msg_headers = {
        MX_MESSAGE_TYPE: message_type.encode(DEFAULT_ENCODING),
        MX_SHARDING_KEY: str(sharding_key).encode(DEFAULT_ENCODING),
    }
    if headers:
        msg_headers.update(headers)
    svc = get_service()
    run_sync(partial(svc.send_message, data, message_type, headers, sharding_key))
    # n_partitions = get_mx_partitions()
    # svc.publish(
    #     value=orjson.dumps(data),
    #     stream=MX_STREAM,
    #     partition=sharding_key % n_partitions,
    #     headers=msg_headers,
    # )


def get_mx_partitions() -> int:
    """
    Get number of MX stream partitions
    :return:
    """
    from noc.core.msgstream.config import get_stream

    cfg = get_stream(MX_STREAM)
    return cfg.get_partitions()
