# ----------------------------------------------------------------------
# mx utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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
from noc.models import get_model_id


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
MX_WATCH_FOR_ID = "Watch-For-Id"
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
    ETL_SYNC_FAILED = "etl_sync_failed"
    ETL_SYNC_REPORT = "etl_sync_report"
    NOTIFICATION = "notification"
    OTHER = "other"


@dataclass(frozen=True)
class MetaConfig(object):
    header: str
    is_list: bool = False


CONFIGS = {
    "watch_for": MetaConfig(MX_WATCH_FOR_ID),
    "profile": MetaConfig(MX_PROFILE_ID),
    "groups": MetaConfig(MX_RESOURCE_GROUPS, is_list=True),
    "administrative_domain": MetaConfig(MX_ADMINISTRATIVE_DOMAIN_ID),
    "from": MetaConfig(MX_DATA_ID),
    "labels": MetaConfig(MX_LABELS, is_list=True),
}


class MessageMeta(enum.Enum):
    @property
    def config(self) -> MetaConfig:
        return CONFIGS[self.value]

    WATCH_FOR = "watch_for"
    PROFILE = "profile"
    GROUPS = "groups"
    ADM_DOMAIN = "administrative_domain"
    FROM = "from"
    LABELS = "labels"

    def clean_header_value(self, value: Any) -> bytes:
        if self.config.is_list:
            return MX_H_VALUE_SPLITTER.join(value).encode(DEFAULT_ENCODING)
        return str(value).encode(DEFAULT_ENCODING)


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
NOTIFICATION_METHODS = {"mail": b"mailsender", "tg": b"tgsender"}

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

    Attrs:
        data: Data for transmit
        message_type: Message type
        headers: additional message headers
        sharding_key: Key for sharding over MX services
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
    Attrs:
        subject: Notification Title
        body: Notification body
        to: notification address
        notification_method: Notification method (for to param)
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
    """Get number of MX stream partitions"""
    from noc.core.msgstream.config import get_stream

    cfg = get_stream(MX_STREAM)
    return cfg.get_partitions()


def get_subscription_id(o) -> str:
    return f"m:{get_model_id(o)}:{o.id}"
