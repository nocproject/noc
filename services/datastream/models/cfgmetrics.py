# ----------------------------------------------------------------------
# cfgmetric datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Any

# Third-party modules
from pydantic import BaseModel


class CollectorMapRule(BaseModel):
    collector: str
    field: str
    sender: str = Any
    allow_partial_match: bool = False
    aliases: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    preference: int = 0


class CfgMetric(BaseModel):
    id: str
    table: str
    field: str
    rules: Optional[List[CollectorMapRule]] = None
