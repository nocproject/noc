# ----------------------------------------------------------------------
# alarm datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import RemoteSystemItem


class ManagedObjectProfileItem(BaseModel):
    id: str
    name: str


class ManagedObjectItem(BaseModel):
    id: str
    name: str
    object_profile: ManagedObjectProfileItem
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class AlarmClassItem(BaseModel):
    id: str
    name: str


class EscalationItem(BaseModel):
    timestamp: datetime.datetime
    tt_id: str
    tt_system: str
    error: str | None
    close_timestamp: datetime.datetime | None
    close_error: str | None


class ServiceProfileItem(BaseModel):
    id: str
    name: str


class ServiceSummaryItem(BaseModel):
    profile: ServiceProfileItem
    summary: int


class SubscriberProfileItem(BaseModel):
    id: str
    name: str


class SubscriberSummaryItem(BaseModel):
    profile: SubscriberProfileItem
    summary: int


class AlarmDataStreamItem(BaseModel):
    id: str
    change_id: str
    timestamp: datetime.datetime
    severity: int
    reopens: int
    labels: list[str] | None
    tags: list[str] | None
    root: str | None
    clear_timestamp: str | None
    managed_object: ManagedObjectItem
    alarm_class: AlarmClassItem
    vars: dict[str, str | int]
    escalation: EscalationItem | None
    direct_services: list[ServiceSummaryItem]
    total_services: list[ServiceSummaryItem]
    direct_subscribers: list[SubscriberSummaryItem]
    total_subscribers: list[SubscriberSummaryItem]
