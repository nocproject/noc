# ----------------------------------------------------------------------
# Container loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.container import Container
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object


class ContainerLoader(BaseLoader):
    """
    Inventory container loader
    """

    name = "container"
    model = Object
    data_model = Container

    CONTAINER_MODEL = "Group"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_map = {}
        self.containers = {}  # Path -> Object

    def get_model(self, model):
        if model not in self.model_map:
            self.model_map[model] = ObjectModel.objects.get(name=model)
        return self.model_map[model]

    def get_container(self, path):
        if path not in self.containers:
            pp = path.split(" | ")
            # Find object
            c = Object.get_by_path(pp, hints=self.mappings)
            if c:
                self.containers[path] = c
            else:
                self.logger.debug("Create container: %s", path)
                if " | " in path:
                    parent = self.get_container(path.rsplit(" | ", 1)[0])
                else:
                    parent = None
                self.containers[path] = Object(
                    name=pp[-1],
                    container=parent.id if parent else None,
                    model=self.get_model(self.CONTAINER_MODEL),
                )
                self.containers[path].save()
        return self.containers[path]

    def create_object(self, v):
        o = self.model(
            name=v["name"],
            container=self.get_container(v["path"]).id,
            model=self.get_model(v["model"]),
            labels=self.tags,
        )
        if v.get("lon") and v.get("lat"):
            o.set_data("geopoint", "x", v["lon"])
            o.set_data("geopoint", "y", v["lat"])
        if v.get("addr_id") and v.get("addr_text"):
            o.set_data("address", "id", v["addr_id"])
            o.set_data("address", "text", v["addr_text"])
        if v.get("adm_contact_text"):
            o.set_data("contacts", "administrative", v["adm_contact_text"])
        if v.get("tech_contact_text"):
            o.set_data("contacts", "technical", v["tech_contact_text"])
        if v.get("billing_contact_text"):
            o.set_data("contacts", "billing", v["tech_contact_text"])
        o.save()
        return o

    def change_object(self, object_id, v, change_object=None, **kwargs):
        o = self.model.objects.get(pk=object_id)
        if v.get("name"):
            o.name = v.get("name")
        if v.get("model"):
            o.model = self.get_model(v["model"])
        if v.get("path"):
            o.container = self.get_container(v["path"]).id
        if v.get("lon"):
            o.set_data("geopoint", "x", v["lon"])
        if v.get("lat"):
            o.set_data("geopoint", "y", v["lat"])
        if v.get("addr_id"):
            o.set_data("address", "id", v["addr_id"])
        if v.get("addr_text"):
            o.set_data("address", "text", v["addr_text"])
        if v.get("adm_contact_text"):
            o.set_data("contacts", "administrative", v["adm_contact_text"])
        if v.get("tech_contact_text"):
            o.set_data("contacts", "technical", v["tech_contact_text"])
        if v.get("adm_contact_text"):
            o.set_data("contacts", "administrative", v["adm_contact_text"])
        if v.get("billing_contact_text"):
            o.set_data("contacts", "billing", v["billing_contact_text"])
        o.save()
