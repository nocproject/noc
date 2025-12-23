# ----------------------------------------------------------------------
# MaintenanceModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

# NOC modules
from .base import BaseModel


class Maintenance(BaseModel):
    id: str
    subject: str
    start: datetime.datetime
    stop: datetime.datetime
    contacts: List[str]
    type: Optional[str] =None
    description: Optional[str] = None
    # Deadline
    suppress_alarms: bool = True
