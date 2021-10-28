# ----------------------------------------------------------------------
# administrativedomain datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import RemoteSystemItem


class AdmDomainDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    parent: Optional[str]
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]
