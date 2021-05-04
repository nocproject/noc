# ----------------------------------------------------------------------
# DefaultObjectItem
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


class PointItem(BaseModel):
    x: float
    y: float


class DefaultObjectItem(BaseModel):
    id: str
    name: str
    model: Reference
    container: Optional[Reference]
    layer: Optional[Reference]
    point: Optional[PointItem]
    labels: List[LabelItem]
    effective_labels: List[LabelItem]
    remote_system: Optional[Reference]
    remote_id: Optional[str]
    bi_id: str


class FormObjectItem(BaseModel):
    name: str
    model: Reference
    container: Optional[Reference]
    labels: List[LabelItem]
