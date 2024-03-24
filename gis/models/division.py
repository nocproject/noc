# ---------------------------------------------------------------------
# Division object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
import bson
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DictField,
    BooleanField,
    DateTimeField,
    IntField,
    ListField,
    ReferenceField,
)
import cachetools

# NOC modules
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.comp import smart_text
from noc.core.model.decorator import on_delete_check
from noc.main.models.remotesystem import RemoteSystem

id_lock = Lock()


@Label.model
@on_delete_check(
    check=[("gis.Street", "parent"), ("gis.Division", "parent"), ("gis.Building", "adm_division")]
)
class Division(Document):
    meta = {
        "collection": "noc.divisions",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "data", "name", "remote_id", "labels", "effective_labels"],
    }
    # Division type
    type = StringField(default="A", choices=[("A", "Administrative")])
    #
    parent = PlainReferenceField("self")
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Division level
    level = IntField()
    # Additional data
    # Depends on importer
    data = DictField()
    #
    start_date = DateTimeField()
    end_date = DateTimeField()
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Division"]:
        return Division.objects.filter(id=oid).first()

    def __str__(self):
        if self.short_name:
            return self.short_name
        else:
            return self.name

    def get_children(self):
        return Division.objects.filter(parent=self.id)

    @classmethod
    def get_top(cls, type="A"):
        return Division.objects.filter(parent__exists=False, type=type)

    def get_buildings(self):
        from .building import Building

        return Building.objects.filter(adm_division=self.id).order_by("sort_order")

    @classmethod
    def update_levels(cls):
        """
        Update divisions levels
        """

        def _update(root, level):
            if root.level != level:
                root.level = level
                root.save()
            for c in root.get_children():
                _update(c, level + 1)

        for d in cls.get_top():
            _update(d, 0)

    @property
    def full_path(self):
        r = [smart_text(self)]
        p = self.parent
        while p:
            r = [smart_text(p)] + r
            p = p.parent
        return " | ".join(r)

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_division")
