# ----------------------------------------------------------------------
# resourcegroup datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.datastream.base import DataStream, RemoteSystemItem
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.comp import smart_text


def qs(s):
    if not s:
        return ""
    return smart_text(s)


class TechnologyItem(BaseModel):
    id: str
    name: str


class ResourceGroupDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    technology: TechnologyItem
    parent: Optional[str]
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class ResourceGroupDataStream(DataStream):
    name = "resourcegroup"
    model = ResourceGroupDataStreamItem

    @classmethod
    def get_object(cls, id):
        rg = ResourceGroup.objects.filter(id=id).first()
        if not rg:
            raise KeyError()
        r = {
            "id": str(rg.id),
            "name": qs(rg.name),
            "technology": {"id": str(rg.technology.id), "name": qs(rg.technology.name)},
        }
        if rg.parent:
            r["parent"] = str(rg.parent.id)
        cls._apply_remote_system(rg, r)
        return r

    @staticmethod
    def _apply_remote_system(mo, r):
        if mo.remote_system:
            r["remote_system"] = {"id": str(mo.remote_system.id), "name": qs(mo.remote_system.name)}
            r["remote_id"] = mo.remote_id
