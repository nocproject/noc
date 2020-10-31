# ----------------------------------------------------------------------
# LinkModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseModel
from .typing import Reference
from .managedobject import ManagedObject


class Link(BaseModel):
    id: str
    source: str
    src_mo: Reference["ManagedObject"]
    src_interface: str
    dst_mo: Reference["ManagedObject"]
    dst_interface: str

    _csv_fields = ["id", "source", "src_mo", "src_interface", "dst_mo", "dst_interface"]
