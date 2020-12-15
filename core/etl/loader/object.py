# ----------------------------------------------------------------------
# Container loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, List

# NOC modules
from .base import BaseLoader
from ..models.object import Object
from noc.inv.models.object import Object as ObjectM
from noc.inv.models.objectmodel import ObjectModel

LOST_AND_FOUND_UUID = "b0fae773-b214-4edf-be35-3468b53b03f2"


class ObjectLoader(BaseLoader):
    """
    Inventory object loader
    """

    name = "object"
    model = ObjectM
    data_model = Object
    fields = [
        "id",
        "name",
        "model",
        "data",
        "container",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["model"] = ObjectModel.get_by_name
        self.l_f_m = ObjectModel.objects.get(uuid=LOST_AND_FOUND_UUID)

    def merge_data(self, o: ObjectM, data: List[Dict[str, Any]]):
        r = {(attr.interface, attr.attr, attr.scope): attr.value for attr in o.data if attr.scope}
        for d in data:
            k = (d["interface"], d["attr"], d["scope"])
            if k in r and d["value"] == r[k]:
                r.pop(k)
                continue
            if k in r:
                self.logger.debug("[%s] Change data: %e", o, d)
                r.pop(k)
                o.set_data(
                    interface=d["interface"],
                    key=d["attr"],
                    value=d["value"],
                    scope=d.get("scope", self.system.name),
                )
            else:
                self.logger.debug("[%s] Set new: %s", o, d)
                o.set_data(
                    interface=d["interface"],
                    key=d["attr"],
                    value=d["value"],
                    scope=d.get("scope", self.system.name),
                )
        for d in r:
            self.logger.debug("[%s] Reset data: %s", o, d)
            o.reset_data(*d)

    def change_object(self, object_id: str, v: Dict[str, Any]):
        self.logger.debug("Changed object: %s", v)
        # See: https://code.getnoc.com/noc/noc/merge_requests/49
        try:
            o: ObjectM = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            self.logger.error("Cannot change %s:%s: Does not exists", self.name, object_id)
            return None
        if "name" in v and v["name"] != o.name:
            o.name = v["name"]
        if "model" in v and v["model"] != o.model.name:
            o.model = ObjectModel.get_by_name(v["model"])
        if (not o.container and v.get("container")) or (
            v.get("container") and v["container"] != str(o.container.id)
        ):
            o.container = self.model.get_by_id(v["container"])
        if not (o.data and v["data"]):
            self.merge_data(o, v["data"])
        o.save()
        return o
