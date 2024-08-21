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


def clean_model(name):
    r = ObjectModel.get_by_name(name)
    if not r:
        raise ValueError(f"Model {name} not found")
    return r


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
        # @todo check None model
        self.clean_map["model"] = clean_model
        self.l_f_m = ObjectModel.objects.get(uuid=LOST_AND_FOUND_UUID)

    def merge_data(self, o: ObjectM, data: List[Dict[str, Any]]):
        # @todo add test to merge_data
        r = {(attr.interface, attr.attr, attr.scope): attr.value for attr in o.data if attr.scope}
        self.logger.debug("Merge data object: %s, Data: %s", o.data, data)
        for d in data:
            k = (d["interface"], d["attr"], d["scope"])
            if k in r and d["value"] == r[k]:
                r.pop(k)
                continue
            if k in r:
                self.logger.debug("[%s] Change data: %s", o, d)
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

    def change_object(
        self,
        object_id: str,
        v: Dict[str, Any],
        inc_changes: Dict[str, Dict[str, List]] = None,
        **kwargs,
    ):
        self.logger.debug("Changed object: %s", v)
        # See: https://code.getnoc.com/noc/noc/merge_requests/49
        try:
            o: ObjectM = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            self.logger.error("Cannot change %s:%s: Does not exists", self.name, object_id)
            return None
        if "name" in v and v["name"] != o.name:
            o.name = v["name"]
        if "model" in v and isinstance(v["model"], str):
            # Fix if model is name?
            v["model"] = ObjectModel.get_by_name(v["model"])
        if "model" in v and v["model"].name != o.model.name:
            o.model = v["model"]
        if (not o.parent and v.get("parent")) or (
            v.get("parent") and v["parent"] != str(o.parent.id)
        ):
            o.parent = v["parent"]
        if "data" not in v or not v["data"]:
            # reset only RemoteSystem Scope
            # o.data = []
            for item in o.data:
                if item.scope == self.system.name:
                    o.reset_data(interface=item.interface, key=item.attr, scope=self.system.name)
        elif v["data"]:
            self.merge_data(o, v["data"])
        o.save()
        return o
