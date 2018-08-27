# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# resourcegroup datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.inv.models.resourcegroup import ResourceGroup


def qs(s):
    if not s:
        return ""
    return s.encode("utf-8")


class ResourceGroupDataStream(DataStream):
    name = "resourcegroup"

    @classmethod
    def get_object(cls, id):
        rg = ResourceGroup.objects.filter(id=id).first()
        if not rg:
            raise KeyError()
        r = {
            "id": str(rg.id),
            "name": qs(rg.name),
            "technology": {
                "id": str(rg.technology.id),
                "name": qs(rg.technology.name)
            }
        }
        if rg.parent:
            r["parent"] = str(rg.parent.id)
        cls._apply_remote_system(rg, r)
        return r

    @staticmethod
    def _apply_remote_system(mo, r):
        if mo.remote_system:
            r["remote_system"] = {
                "id": str(mo.remote_system.id),
                "name": qs(mo.remote_system.name)
            }
            r["remote_id"] = mo.remote_id
