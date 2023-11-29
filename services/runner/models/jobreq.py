# ----------------------------------------------------------------------
# Job request
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict
import datetime

# Third party modules
from pydantic import BaseModel


class InputMapping(BaseModel):
    name: str
    value: str


class OutputMapping(BaseModel):
    name: str
    value: str


class JobRequest(BaseModel):
    """
    Pipeline job.

    Attributes:
    """

    name: str
    action: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    allow_fail: bool = False
    locks: Optional[List[str]] = None
    inputs: Optional[List[InputMapping]] = None
    outputs: Optional[List[OutputMapping]] = None
    require_approval: bool = False
    depends_on: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    after: Optional[datetime.datetime] = None
    deadline: Optional[datetime.datetime] = None
    jobs: Optional[List["JobRequest"]] = None
