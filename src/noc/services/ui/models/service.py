# ----------------------------------------------------------------------
# DefaultServiceItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

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
    labels: list[LabelItem]
    effective_labels: list[LabelItem]
    static_service_groups: list[Reference]
    effective_service_groups: list[Reference]
    static_client_groups: list[Reference]
    effective_client_groups: list[Reference]
    parent: Reference | None = None
    subscriber: Reference | None = None
    supplier: Reference | None = None
    description: str | None = None
    agreement_id: str | None = None
    order_id: str | None = None
    stage_id: str | None = None
    stage_name: str | None = None
    stage_start: datetime.datetime | None = None
    account_id: str | None = None
    address: str | None = None
    managed_object: Reference | None = None
    nri_port: str | None = None
    remote_system: Reference | None = None
    remote_id: str | None = None
    bi_id: int | None = None


class FormServiceItem(BaseModel):
    profile: Reference
    parent: Reference | None = None
    subscriber: Reference | None = None
    supplier: Reference | None = None
    description: str | None = None
    agreement_id: str | None = None
    order_id: str | None = None
    stage_id: str | None = None
    stage_name: str | None = None
    stage_start: str | None = None
    account_id: str | None = None
    address: str | None = None
    managed_object: Reference | None = None
    nri_port: str | None = None
    labels: list[str] | None = None
    static_service_groups: list[Reference] | None = None
    static_client_groups: list[Reference] | None = None


class PreviewServiceItem(BaseModel):
    id: str
    profile: Reference
    parent: Reference | None = None
    state: Reference
    state_changed: datetime.datetime | None = None
    description: str
    address: str
