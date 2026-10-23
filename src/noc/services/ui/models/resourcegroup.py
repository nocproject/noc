# ----------------------------------------------------------------------
# DefaultResourceGroupItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from ..models.label import LabelItem


class DefaultResourceGroupItem(BaseModel):
    id: str
    name: str
    technology: Reference
    bi_id: str
    parent: Reference | None = None
    description: str | None = None
    dynamic_service_labels: list[str] | None = None
    dynamic_client_labels: list[str] | None = None
    remote_system: Reference | None = None
    remote_id: str | None = None
    # Labels
    labels: list[LabelItem] | None = None
    effective_labels: list[LabelItem] | None = None


class FormResourceGroupItem(BaseModel):
    name: str
    technology: Reference
    parent: Reference | None = None
    description: str | None = None
    dynamic_service_labels: list[str] | None = None
    dynamic_client_labels: list[str] | None = None
    labels: list[str] | None = None
