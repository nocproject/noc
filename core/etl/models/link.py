# ----------------------------------------------------------------------
# LinkModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseModel


class LinkModel(BaseModel):
    id: str
    source: str
    src_mo: str
    src_interface: str
    dst_mo: str
    dst_interface: str

    _csv_fields = ["id", "source", "src_mo", "src_interface", "dst_mo", "dst_interface"]
