# ----------------------------------------------------------------------
# DefaultServiceItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from ..models.label import LabelItem


class DefaultServiceItem(BaseModel):
    id: str
    profile: Reference
    ts: datetime.datetime
    state: Reference
    state_changed: datetime.datetime
    parent: Optional[Reference]
    subscriber: Optional[Reference]
    supplier: Optional[Reference]
    description: Optional[str]
    agreement_id: Optional[str]
    order_id: Optional[str]
    stage_id: Optional[str]
    stage_name: Optional[str]
    stage_start: Optional[datetime.datetime]
    account_id: Optional[str]
    address: Optional[str]
    managed_object: Optional[Reference]
    nri_port: Optional[str]
    labels: List[LabelItem]
    effective_labels: List[LabelItem]
    static_service_groups: List[Reference]
    effective_service_groups: List[Reference]
    static_client_groups: List[Reference]
    effective_client_groups: List[Reference]
    remote_system: Optional[Reference]
    remote_id: Optional[str]
    bi_id: Optional[int]


class FormServiceItem(BaseModel):
    profile: Reference
    parent: Optional[Reference]
    subscriber: Optional[Reference]
    supplier: Optional[Reference]
    description: Optional[str]
    agreement_id: Optional[str]
    order_id: Optional[str]
    stage_id: Optional[str]
    stage_name: Optional[str]
    stage_start: Optional[str]
    account_id: Optional[str]
    address: Optional[str]
    managed_object: Optional[Reference]
    nri_port: Optional[str]
    labels: Optional[List[str]]
    static_service_groups: Optional[List[Reference]]
    static_client_groups: Optional[List[Reference]]


class PreviewServiceItem(BaseModel):
    id: str
    profile: Reference
    parent: Optional[Reference]
    state: Reference
    state_changed: Optional[datetime.datetime]
    description: str
    address: str
