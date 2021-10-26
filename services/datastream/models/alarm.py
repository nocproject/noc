# ----------------------------------------------------------------------
# alarm datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Dict, Union

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
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class AlarmClassItem(BaseModel):
    id: str
    name: str


class EscalationItem(BaseModel):
    timestamp: datetime.datetime
    tt_id: str
    tt_system: str
    error: Optional[str]
    close_timestamp: Optional[datetime.datetime]
    close_error: Optional[str]


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
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    root: Optional[str]
    clear_timestamp: Optional[str]
    managed_object: ManagedObjectItem
    alarm_class: AlarmClassItem
    vars: Dict[str, Union[str, int]]
    escalation: Optional[EscalationItem]
    direct_services: List[ServiceSummaryItem]
    total_services: List[ServiceSummaryItem]
    direct_subscribers: List[SubscriberSummaryItem]
    total_subscribers: List[SubscriberSummaryItem]
