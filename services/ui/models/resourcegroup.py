# ----------------------------------------------------------------------
# DefaultResourceGroupItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

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
    parent: Optional[Reference] = None
    description: Optional[str] = None
    dynamic_service_labels: Optional[List[str]] = None
    dynamic_client_labels: Optional[List[str]] = None
    remote_system: Optional[Reference] = None
    remote_id: Optional[str] = None
    # Labels
    labels: Optional[List[LabelItem]] = None
    effective_labels: Optional[List[LabelItem]] = None


class FormResourceGroupItem(BaseModel):
    name: str
    technology: Reference
    parent: Optional[Reference] = None
    description: Optional[str] = None
    dynamic_service_labels: Optional[List[str]] = None
    dynamic_client_labels: Optional[List[str]] = None
    labels: Optional[List[str]] = None
