# ----------------------------------------------------------------------
# mx utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
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
# Object data
MX_ADMINISTRATIVE_DOMAIN_ID = "Administrative-Domain-Id"
MX_PROFILE_ID = "Profile-Id"
MX_LABELS = "Labels"
MX_RESOURCE_GROUPS = "Resource-Group-Ids"
# Notification headers
MX_TO = "To"
MX_NOTIFICATION = b"notification"
MX_NOTIFICATION_DELAY = "Notification-Delay-Sec"
MX_NOTIFICATION_CHANNEL = "Notification-Channel"
MX_NOTIFICATION_METHOD = "Notification-Method"
MX_NOTIFICATION_GROUP_ID = "Notification-Group-Id"
MX_LANG = "Language"
KAFKA_PARTITION = "Kafka-Partition"
#
MX_H_VALUE_SPLITTER = ";"
# Available message types


class MessageType(enum.Enum):
    ALARM = "alarm"
    MANAGEDOBJECT = "managedobject"
    REBOOT = "reboot"
    METRICS = "metrics"
    SNMPTRAP = "snmptrap"
    SYSLOG = "syslog"
    EVENT = "event"
    INTERFACE_STATUS_CHANGE = "interface_status_change"
    CONFIG_CHANGED = "config_changed"
    OBJECT_NEW = "object_new"
    OBJECT_DELETED = "object_deleted"
    VERSION_CHANGED = "version_changed"
    CONFIG_POLICY_VIOLATION = "config_policy_violation"
    DIAGNOSTIC_CHANGE = "diagnostic_change"
    NOTIFICATION = "notification"
    OTHER = "other"


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
NOTIFICATION_METHODS = {"mail": b"mailsender", "tg": b"tgsender", "icq": b"icqsender"}

_mx_partitions: Optional[int] = None
_mx_lock = Lock()


def send_message(
    data: Any,
    message_type: MessageType,
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
        MX_MESSAGE_TYPE: message_type.value,
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


def send_notification(
    subject: str,
    body: str,
    to: str,  # ? method::/address
    notification_method: str = "mail",
    **kwargs,
):
    """
    Send notification to notification_group ot address
    :param subject: Notification Title
    :param body: Notification body
    :param to: notification address
    :param notification_method: Notification method (for to param)
    :return:
    """
    if notification_method not in NOTIFICATION_METHODS:
        raise ValueError("Unknown notification method: %s" % notification_method)
    msg_headers = {
        MX_MESSAGE_TYPE: MessageType.NOTIFICATION.value.encode(),
        MX_NOTIFICATION_CHANNEL: NOTIFICATION_METHODS[notification_method],
        MX_TO: to.encode(DEFAULT_ENCODING),
    }
    svc = get_service()
    data = {"body": body, "subject": subject, "address": to}
    if kwargs:
        data |= kwargs
    run_sync(partial(svc.send_message, data, MessageType.NOTIFICATION, msg_headers))


def get_mx_partitions() -> int:
    """
    Get number of MX stream partitions
    :return:
    """
    from noc.core.msgstream.config import get_stream

    cfg = get_stream(MX_STREAM)
    return cfg.get_partitions()
