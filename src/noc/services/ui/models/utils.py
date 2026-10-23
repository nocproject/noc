# ----------------------------------------------------------------------
# Model utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class Reference(BaseModel):
    id: str
    label: str | None = None


class LabelItem(BaseModel):
    id: str
    label: str
    # For tree structure fields
    parent: Reference | None = None
    level: int | None = None
    has_children: bool | None = None


class SummaryItem(BaseModel):
    id: str
    label: str
    count: int
