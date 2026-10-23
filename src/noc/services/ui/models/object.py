# ----------------------------------------------------------------------
# DefaultObjectItem
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


class PointItem(BaseModel):
    x: float
    y: float


class DefaultObjectItem(BaseModel):
    id: str
    name: str
    model: Reference
    bi_id: str
    labels: list[LabelItem]
    effective_labels: list[LabelItem]
    container: Reference | None = None
    layer: Reference | None = None
    point: PointItem | None = None
    remote_system: Reference | None = None
    remote_id: str | None = None


class FormObjectItem(BaseModel):
    name: str
    model: Reference
    labels: list[LabelItem]
    container: Reference | None = None
