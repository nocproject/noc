# ----------------------------------------------------------------------
# resourcegroup datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import RemoteSystemItem


class TechnologyItem(BaseModel):
    id: str
    name: str


class ResourceGroupDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    technology: TechnologyItem
    parent: str | None
    remote_system: RemoteSystemItem | None
    remote_id: str | None
