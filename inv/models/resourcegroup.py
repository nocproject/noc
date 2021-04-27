# ----------------------------------------------------------------------
# ResourceGroup model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import threading
from typing import List

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField
from pymongo import UpdateMany
import cachetools

# NOC modules
from noc.config import config
from noc.models import get_model, is_document
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.datastream.decorator import datastream
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from .technology import Technology

id_lock = threading.Lock()


@Label.model
@bi_sync
@datastream
@on_save
@on_delete_check(
    check=[
        ("inv.ResourceGroup", "parent"),
        # sa.ManagedObject
        ("sa.ManagedObject", "static_service_groups"),
        ("sa.ManagedObject", "effective_service_groups"),
        ("sa.ManagedObject", "static_client_groups"),
        ("sa.ManagedObject", "effective_client_groups"),
        # sa.ManagedObjectSelector
        ("sa.ManagedObjectSelector", "filter_service_group"),
        ("sa.ManagedObjectSelector", "filter_client_group"),
        # phone.PhoneRange
        ("phone.PhoneRange", "static_service_groups"),
        ("phone.PhoneRange", "effective_service_groups"),
        ("phone.PhoneRange", "static_client_groups"),
        ("phone.PhoneRange", "effective_client_groups"),
        # phone.PhoneNumber
        ("phone.PhoneNumber", "static_service_groups"),
        ("phone.PhoneNumber", "effective_service_groups"),
        ("phone.PhoneNumber", "static_client_groups"),
        ("phone.PhoneNumber", "effective_client_groups"),
        # sa.Service
        ("sa.Service", "static_service_groups"),
        ("sa.Service", "effective_service_groups"),
        ("sa.Service", "static_client_groups"),
        ("sa.Service", "effective_client_groups"),
    ]
)
class ResourceGroup(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """

    meta = {
        "collection": "resourcegroups",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "dynamic_service_labels",
            "dynamic_client_labels",
        ],
    }

    # Group | Name
    name = StringField()
    technology = PlainReferenceField(Technology)
    parent = PlainReferenceField("inv.ResourceGroup")
    description = StringField()
    dynamic_service_labels = ListField(StringField())
    dynamic_client_labels = ListField(StringField())
    # @todo: FM integration
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s (%s)" % (self.name, self.technology.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ResourceGroup.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return ResourceGroup.objects.filter(bi_id=id).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_resourcegroup:
            yield "resourcegroup", self.id

    @property
    def has_children(self):
        return bool(ResourceGroup.objects.filter(parent=self.id).only("id").first())

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_resourcegroup")

    def on_save(self):
        if (
            hasattr(self, "_changed_fields")
            and "dynamic_service_labels" in self._changed_fields
            and self.technology.service_model
        ):
            self.unset_service_group(self.technology.service_model)
        if (
            hasattr(self, "_changed_fields")
            and "dynamic_client_labels" in self._changed_fields
            and self.technology.client_model
        ):
            self.unset_cient_group(self.technology.client_model)

    def unset_service_group(self, model_id: str):
        from django.db import connection

        model = get_model(model_id)
        if is_document(model):
            coll = model._get_collection()
            coll.bulk_write(
                [
                    UpdateMany[
                        {"effective_service_groups": {"$in": [self.id]}},
                        {"$pull": {"effective_service_groups": {"$in": [self.id]}}},
                    ]
                ]
            )
        else:
            sql = f"UPDATE {model._meta.db_table} SET effective_service_groups=array_remove(effective_service_groups, '{str(self.id)}') WHERE '{str(self.id)}'=ANY (effective_service_groups)"
            cursor = connection.cursor()
            cursor.execute(sql)

    def unset_cient_group(self, model_id: str):
        from django.db import connection

        model = get_model(model_id)
        if is_document(model):
            coll = model._get_collection()
            coll.bulk_write(
                [
                    UpdateMany[
                        {"effective_client_groups": {"$in": [self.id]}},
                        {"$pull": {"effective_client_groups": {"$in": [self.id]}}},
                    ]
                ]
            )
        else:
            sql = f"UPDATE {model._meta.db_table} SET effective_client_groups=array_remove(effective_client_groups, '{str(self.id)}') WHERE '{str(self.id)}'=ANY (effective_service_groups)"
            cursor = connection.cursor()
            cursor.execute(sql)

    @classmethod
    def get_dynamic_service_groups(cls, labels: List[str], model: str) -> List[str]:
        coll = cls._get_collection()
        r = []
        for rg in coll.aggregate(
            [
                {"$match": {"dynamic_service_labels": {"$in": labels}}},
                {
                    "$lookup": {
                        "from": "technologies",
                        "localField": "technology",
                        "foreignField": "_id",
                        "as": "tech",
                    }
                },
                {
                    "$match": {
                        "tech.service_model": model,
                    }
                },
                {
                    "$project": {
                        "bool_f": {
                            "$allElementsTrue": [
                                {
                                    "$map": {
                                        "input": "$dynamic_service_labels",
                                        "as": "item",
                                        "in": {"$in": ["$$item", labels]},
                                    }
                                }
                            ]
                        }
                    }
                },
                {"$match": {"bool_f": True}},
            ]
        ):
            r.append(rg["_id"])
        return r

    @classmethod
    def get_dynamic_client_groups(cls, labels: List[str], model: str) -> List[str]:
        coll = cls._get_collection()
        r = []
        for rg in coll.aggregate(
            [
                {"$match": {"dynamic_client_labels": {"$in": labels}}},
                {
                    "$lookup": {
                        "from": "technologies",
                        "localField": "technology",
                        "foreignField": "_id",
                        "as": "tech",
                    }
                },
                {
                    "$match": {
                        "tech.client_model": model,
                    }
                },
                {
                    "$project": {
                        "bool_f": {
                            "$allElementsTrue": [
                                {
                                    "$map": {
                                        "input": "dynamic_client_labels",
                                        "as": "item",
                                        "in": {"$in": ["$$item", labels]},
                                    }
                                }
                            ]
                        }
                    }
                },
                {"$match": {"bool_f": True}},
            ]
        ):
            rg.append(rg["_id"])
        return r
