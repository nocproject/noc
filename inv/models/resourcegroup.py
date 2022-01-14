# ----------------------------------------------------------------------
# ResourceGroup model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import threading
from typing import List, Union, Optional

# Third-party modules
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, LongField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError
from pymongo import UpdateMany
import cachetools

# NOC modules
from noc.config import config
from noc.models import get_model, is_document
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save, tree
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from .technology import Technology

id_lock = threading.Lock()
rx_labels_lock = threading.Lock()

_path_cache = cachetools.TTLCache(maxsize=100, ttl=60)


def check_rg_parent(parent: "ResourceGroup"):
    if not parent.technology.allow_children:
        raise ValidationError(f"[{parent}] Parent technology is not allowed children")


class MatchLabels(EmbeddedDocument):
    labels = ListField(StringField())

    def __str__(self):
        return ", ".join(self.labels)

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


@tree()
@Label.match_labels("resourcegroup", allowed_op={"="}, parent_op={"<"})
@Label.model
@bi_sync
@change
@on_save
@on_delete_check(
    check=[
        ("inv.ResourceGroup", "parent"),
        # sa.ManagedObject
        ("sa.ManagedObject", "static_service_groups"),
        ("sa.ManagedObject", "static_client_groups"),
        # sa.ManagedObjectSelector
        ("sa.ManagedObjectSelector", "filter_service_group"),
        ("sa.ManagedObjectSelector", "filter_client_group"),
        # phone.PhoneRange
        ("phone.PhoneRange", "static_service_groups"),
        ("phone.PhoneRange", "static_client_groups"),
        # phone.PhoneNumber
        ("phone.PhoneNumber", "static_service_groups"),
        ("phone.PhoneNumber", "static_client_groups"),
        # sa.Service
        ("sa.Service", "static_service_groups"),
        ("sa.Service", "static_client_groups"),
        # SA
        ("sa.CommandSnippet", "resource_group"),
        ("sa.ObjectNotification", "resource_group"),
        # FM
        ("fm.AlarmDiagnosticConfig", "resource_group"),
        ("fm.AlarmEscalation", "escalations__resource_group"),
        ("fm.AlarmTrigger", "resource_group"),
        ("fm.EventTrigger", "resource_group"),
        #
        ("vc.VCDomainProvisioningConfig", "resource_group"),
    ],
    clean=[
        # ("sa.ManagedObject", "effective_service_groups"),
        # ("sa.ManagedObject", "effective_client_groups"),
        # ("phone.PhoneRange", "effective_service_groups"),
        # ("phone.PhoneRange", "effective_client_groups"),
        # ("phone.PhoneNumber", "effective_service_groups"),
        # ("phone.PhoneNumber", "effective_client_groups"),
        # ("sa.Service", "effective_service_groups"),
        # ("sa.Service", "effective_client_groups"),
    ],
    clean_lazy_labels="resourcegroup",
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
            "dynamic_service_labels.labels",
            "dynamic_client_labels.labels",
            "labels",
            "effective_labels",
        ],
    }

    # Group | Name
    name = StringField()
    technology = PlainReferenceField(Technology)
    parent = PlainReferenceField("inv.ResourceGroup", validation=check_rg_parent)
    description = StringField()
    dynamic_service_labels = ListField(EmbeddedDocumentField(MatchLabels))
    dynamic_client_labels = ListField(EmbeddedDocumentField(MatchLabels))
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
    _nested_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _lazy_labels_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

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

    @classmethod
    def _reset_caches(cls, id):
        try:
            del cls._id_cache[
                str(id),  # Tuple
            ]
        except KeyError:
            pass

    @cachetools.cached(_path_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_resourcegroup:
            yield "resourcegroup", self.id

    @property
    def has_children(self):
        return bool(ResourceGroup.objects.filter(parent=self.id).only("id").first())

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_nested_cache"), lock=lambda _: id_lock)
    def get_nested_ids(cls, resource_group):
        """
        Return id of this and all nested segments
        :return:
        """
        if hasattr(resource_group, "id"):
            resource_group = resource_group.id
        elif isinstance(resource_group, str):
            resource_group = bson.ObjectId(resource_group)

        # $graphLookup hits 100Mb memory limit. Do not use it
        seen = {resource_group}
        wave = {resource_group}
        max_level = 10
        coll = ResourceGroup._get_collection()
        for _ in range(max_level):
            # Get next wave
            wave = (
                set(d["_id"] for d in coll.find({"parent": {"$in": list(wave)}}, {"_id": 1})) - seen
            )
            if not wave:
                break
            seen |= wave
        return list(seen)

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_resourcegroup")

    def on_save(self):
        self._reset_caches(self.id)
        if (
            hasattr(self, "_changed_fields")
            and "dynamic_service_labels" in self._changed_fields
            and self.technology.service_model
        ) or (not hasattr(self, "_changed_fields") and self.dynamic_service_labels):
            self.unset_service_group(self.technology.service_model)
            self.add_service_group(self.technology.service_model)
        if (
            hasattr(self, "_changed_fields")
            and "dynamic_client_labels" in self._changed_fields
            and self.technology.client_model
        ) or (not hasattr(self, "_changed_fields") and self.dynamic_client_labels):
            self.unset_client_group(self.technology.client_model)
            self.add_client_group(self.technology.client_model)

    @staticmethod
    def _remove_group(
        model_id: str,
        group_id: Union[str, bson.ObjectId],
        is_client: bool = False,
    ):
        """

        :param model_id: System model_id
        :param group_id: ResourceGroup ID
        :param is_client: Add to Client Groups
        :return:
        """
        from django.db import connection

        if isinstance(group_id, str):
            group_id = bson.ObjectId(group_id)

        model = get_model(model_id)
        group_field = "effective_service_groups" if not is_client else "effective_client_groups"
        if is_document(model):
            coll = model._get_collection()
            coll.bulk_write(
                [
                    UpdateMany(
                        {group_field: {"$in": [group_id]}},
                        {"$pull": {group_field: {"$in": [group_id]}}},
                    )
                ]
            )
        else:
            sql = f"UPDATE {model._meta.db_table} SET {group_field}=array_remove({group_field}, '{str(group_id)}') WHERE '{str(group_id)}'=ANY ({group_field})"
            cursor = connection.cursor()
            cursor.execute(sql)

    @staticmethod
    def _add_group(
        model_id: str,
        group_id: Union[str, bson.ObjectId],
        labels: List[str],
        is_client: bool = False,
    ):
        """

        :param model_id: System model_id
        :param group_id: ResourceGroup ID
        :param labels: Match Labels
        :param is_client: Add to Client Groups
        :return:
        """
        from django.db import connection

        if isinstance(group_id, str):
            group_id = bson.ObjectId(group_id)

        model = get_model(model_id)
        group_field = "effective_service_groups" if not is_client else "effective_client_groups"
        if is_document(model):
            coll = model._get_collection()
            # @todo ALL Match
            coll.bulk_write(
                [
                    UpdateMany(
                        {"effective_labels": {"$in": labels}},
                        {"$addToSet": {group_field: {"$in": [group_id]}}},
                    )
                ]
            )
        else:
            sql = f"UPDATE {model._meta.db_table} SET {group_field}=array_append({group_field}, '{str(group_id)}') WHERE %s::varchar[] <@ effective_labels AND NOT ('{str(group_id)}'= ANY ({group_field}))"
            cursor = connection.cursor()
            cursor.execute(sql, [labels])

    def unset_service_group(self, model_id: str):
        self._remove_group(model_id, self.id)

    def unset_client_group(self, model_id: str):
        self._remove_group(model_id, self.id, is_client=True)

    def add_service_group(self, model_id: str):
        # @todo optimize for one operation
        for ml in self.dynamic_service_labels:
            self._add_group(model_id, self.id, ml.labels)

    def add_client_group(self, model_id: str):
        for ml in self.dynamic_service_labels:
            self._add_group(model_id, self.id, ml.labels, is_client=True)

    @classmethod
    def get_dynamic_service_groups(cls, labels: List[str], model: str) -> List[str]:
        coll = cls._get_collection()
        r = []
        if not model:
            return r
        # print(labels, model)
        for rg in coll.aggregate(
            [
                {"$match": {"dynamic_service_labels.labels": {"$in": labels}}},
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
                            "$anyElementTrue": [
                                {
                                    "$map": {
                                        "input": "$dynamic_service_labels.labels",
                                        "as": "item",
                                        "in": {"$setIsSubset": ["$$item", labels]},
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
        if not model:
            return r
        for rg in coll.aggregate(
            [
                {"$match": {"dynamic_client_labels.labels": {"$in": labels}}},
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
                            "$anyElementTrue": [
                                {
                                    "$map": {
                                        "input": "dynamic_client_labels.labels",
                                        "as": "item",
                                        "in": {"$setIsSubset": ["$$item", labels]},
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

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_lazy_labels_cache"),
        key=lambda x: tuple(x),
        lock=lambda _: rx_labels_lock,
    )
    def get_lazy_labels(cls, resource_groups: List[str]) -> List[str]:
        match_rg = []
        for rg in resource_groups:
            if isinstance(rg, str):
                match_rg += [bson.ObjectId(rg)]
            else:
                match_rg += [rg]
        labels = []
        for rg in cls._get_collection().aggregate(
            [
                {"$project": {"name": 1, "parent": 1}},
                {"$match": {"_id": {"$in": match_rg}}},
                {
                    "$graphLookup": {
                        "from": "resourcegroups",
                        "connectFromField": "parent",
                        "connectToField": "_id",
                        "startWith": "$_id",
                        "as": "_path",
                        "maxDepth": 50,
                    }
                },
            ]
        ):
            labels += [f'noc::resourcegroup::{rg["name"]}::=']
            labels += [
                f'noc::resourcegroup::{rg_path["name"]}::<'
                for rg_path in rg["_path"]
                if rg["_id"] != rg_path["_id"]
            ]
        return labels

    @classmethod
    def iter_lazy_labels(cls, resource_group: "ResourceGroup"):
        for rg in ResourceGroup.objects.filter(id__in=resource_group.get_path()):
            if rg == resource_group:
                # Optimize for less MatchLabels count
                yield f"noc::resourcegroup::{rg.name}::="
                continue
            yield f"noc::resourcegroup::{rg.name}::<"

    @classmethod
    def get_objects_from_expression(cls, s, model_id: Optional[str] = None):
        """
        Get list of Managed Object matching selector expression

        Expression must be string or list.
        Elements must be one of:
        * string starting with @ - treated as selector name
        * string containing numbers - treated as object's id
        * string - managed object name.
        * string - IPv4 or IPv6 address - management address

        Raises ManagedObject.DoesNotExists if object is not found.
        Raises ManagedObjectSelector.DoesNotExists if selector is not found
        :param cls:
        :param s:
        :param model_id:
        :return:
        """
        from noc.core.validators import is_int, is_objectid

        if isinstance(s, int) or isinstance(s, str):
            s = [s]
        if not isinstance(s, list):
            raise ValueError("list required")
        objects = set()
        for so in s:
            if not isinstance(so, str):
                so = str(so)
            # @todo Label expression label1 || label2 && label3 noc- N::pool::MO,
            if so.startswith("@"):
                # ResourceGroup expression: @<resource group name>
                o: "ResourceGroup" = ResourceGroup.objects.get(name=so[1:])
                model = get_model(o.technology.service_model)
                objects |= set(
                    model.objects.filter(
                        effective_service_groups__overlap=ResourceGroup.get_nested_ids(o)
                    )
                )
            elif model_id:
                # @todo Model get_by_q ?
                model = get_model(model_id)
                if not is_document(model) and is_int(so):
                    # Search by id
                    q = {"id": int(so)}
                elif is_document(model) and is_objectid(so):
                    q = {"id": so}
                else:
                    # Search by name
                    q = {"name": so}
                o = model.objects.get(**q)
                objects.add(o)
        return list(objects)
