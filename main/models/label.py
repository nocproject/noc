# ----------------------------------------------------------------------
# Label model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import operator
import re
from typing import Optional, List, Set, Iterable, Dict, Any, Callable, Tuple, Union
from threading import Lock
from collections import defaultdict
from itertools import accumulate
from functools import partial

# Third-party modules
import bson
from pymongo import UpdateMany
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.queryset.visitor import Q as m_Q
from mongoengine.fields import (
    StringField,
    IntField,
    UUIDField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
)
from django.db import connection as pg_connection
import cachetools
import orjson

# NOC modules
from noc.core.model.decorator import on_save, on_delete, on_delete_check
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.change.decorator import change
from noc.main.models.handler import Handler
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.prefixtable import PrefixTable, PrefixTablePrefix
from noc.models import get_model, is_document, get_model_id, LABEL_MODELS
from noc.vc.models.vlanfilter import VLANFilter

from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

MATCH_OPS = {"=", "<", ">", "&"}

MATCH_BADGES = {
    "=": "=",
    "<": "fa-chevron-left",
    ">": "fa-chevron-right",
    "&": "&",
}

REGEX_LABEL_SCOPES = {
    "managedobject_name": ("sa.ManagedObject", "name"),
    "managedobject_address": ("sa.ManagedObject", "address"),
    "managedobject_description": ("sa.ManagedObject", "description"),
    "interface_name": ("inv.Interface", "name"),
    "interface_description": ("inv.Interface", "description"),
    "sensor_local_id": ("inv.Sensor", "local_id"),
}

VLANFILTER_LABEL_SCOPES = {
    "subinterface_tagged_vlans": ("inv.SubInterface", "tagged_vlans"),
    "subinterface_untagged_vlan": ("inv.SubInterface", "untagged_vlan"),
}

PREFIXFILTER_LABEL_SCOPES = {
    "managedobject_address": ("sa.ManagedObject", "address"),
    "subinterface_ipv4_addresses": ("inv.SubInterface", "ipv4_addresses"),
}

id_lock = Lock()
re_lock = Lock()
rx_labels_lock = Lock()
setting_lock = Lock()
allow_model_lock = Lock()

logger = logging.getLogger(__name__)


class RegexItem(EmbeddedDocument):
    regexp = StringField(required=True)
    regexp_compiled = StringField(required=False)
    # Set Multiline flag
    flag_multiline = BooleanField(default=False)
    # Set DotAll flag
    flag_dotall = BooleanField(default=False)
    scope = StringField(choices=list(REGEX_LABEL_SCOPES), required=True)

    def __str__(self):
        return f'{self.scope}: {self.regexp}, {"MULTI" if self.flag_multiline else ""}|{"DOTALL" if self.flag_dotall else ""}'


class VLANFilterItem(EmbeddedDocument):
    vlan_filter = PlainReferenceField(VLANFilter, required=True)
    condition = StringField(choices=["all", "any"])
    scope = StringField(choices=list(VLANFILTER_LABEL_SCOPES), required=True)


class PrefixFilterItem(EmbeddedDocument):
    prefix_table = ForeignKeyField(PrefixTable, required=True)
    condition = StringField(choices=["all", "any"])
    scope = StringField(choices=list(PREFIXFILTER_LABEL_SCOPES), required=True)


@on_save
@change
@on_delete
@on_delete_check(
    check=[
        ("fm.AlarmRule", "match__labels"),
        ("fm.AlarmRule", "match__exclude_labels"),
        ("pm.MetricRule", "match__labels"),
        ("pm.MetricRule", "match__exclude_labels"),
        ("main.MessageRoute", "match__labels"),
        ("main.MessageRoute", "match__exclude_labels"),
        ("sa.ObjectDiagnosticConfig", "match__labels"),
        ("sa.ObjectDiagnosticConfig", "match__exclude_labels"),
        ("sa.CredentialCheckRule", "match__labels"),
        ("sa.CredentialCheckRule", "match__exclude_labels"),
        ("inv.InterfaceProfile", "match_rules__labels"),
        ("inv.ResourceGroup", "dynamic_service_labels__labels"),
        ("inv.ResourceGroup", "dynamic_client_labels__labels"),
        ("sa.ManagedObjectProfile", "match_rules__labels"),
        ("wf.State", "labels"),
    ],
    clean=[
        ("sa.ManagedObject", "labels"),
        ("sa.ManagedObjectProfile", "labels"),
        ("inv.InterfaceProfile", "labels"),
        ("pm.Agent", "labels"),
        ("wf.State", "labels"),
        ("sla.SLAProbe", "labels"),
        ("sla.SLAProfile", "labels"),
    ],
    ignore=[],
)
class Label(Document):
    """
    Scope
    Value
    * Deny rename Labels
    * noc:: - Builtin NOC Labels Scope
    """

    meta = {
        "collection": "labels",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.labels",
        "json_unique_fields": ["name"],
        "indexes": [
            "name",
            "allow_models",
            ("is_matching", "match_regex.scope"),
            (
                "match_vlanfilter.vlan_filter",
                "match_vlanfilter.condition",
                "match_vlanfilter.scope",
            ),
            (
                "match_prefixfilter.prefix_table",
                "match_prefixfilter.condition",
                "match_prefixfilter.scope",
            ),
        ],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    bg_color1 = IntField(default=0x000000)
    fg_color1 = IntField(default=0xFFFFFF)
    bg_color2 = IntField(default=0x000000)
    fg_color2 = IntField(default=0xFFFFFF)
    # Order
    display_order = IntField(default=0)
    # Restrict UI operations
    is_protected = BooleanField(default=False)
    is_autogenerated = BooleanField(default=False)
    is_matching = BooleanField(default=False)
    # For scoped - to propagating settings on own labels
    propagate = BooleanField(default=False)
    # Label scope
    allow_models = ListField(StringField())
    allow_auto_create = BooleanField(default=False)
    # Exposition scope
    expose_metric = BooleanField(default=False)
    expose_datastream = BooleanField(default=False)
    expose_alarm = BooleanField(default=False)
    # Match Condition
    # match_condition = ALL,ANY
    # Regex
    match_regex = ListField(EmbeddedDocumentField(RegexItem))
    # VLAN Filter
    match_vlanfilter = ListField(EmbeddedDocumentField(VLANFilterItem))
    # Prefix Filter
    match_prefixfilter = ListField(EmbeddedDocumentField(PrefixFilterItem))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Caches
    _id_cache = cachetools.TTLCache(maxsize=100, ttl=120)
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=300)
    _setting_cache = cachetools.TTLCache(maxsize=1000, ttl=300)
    _rx_labels_cache = cachetools.TTLCache(maxsize=100, ttl=120)
    _rx_cache = cachetools.TTLCache(maxsize=100, ttl=600)
    # Enable -> Model_id map
    ENABLE_MODEL_ID_MAP = {v: k for k, v in LABEL_MODELS.items()}

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "bg_color1": self.bg_color1,
            "fg_color1": self.fg_color1,
            "bg_color2": self.bg_color2,
            "fg_color2": self.fg_color2,
            # Order
            "display_order": self.display_order,
            #
            "allow_models": list(self.allow_models),
            "allow_auto_create": self.allow_auto_create,
            # Restrict UI operations
            "is_protected": self.is_protected,
            "is_matching": self.is_matching,
            # For scoped - to propagating settings on own labels
            "propagate": self.propagate,
            # Label scope
            # Exposition scope
            "expose_metric": self.expose_metric,
            "expose_datastream": self.expose_datastream,
            "expose_alarm": self.expose_alarm,
            # Regex
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "bg_color1",
                "fg_color1",
                "bg_color2",
                "fg_color2",
                "display_order",
                "allow_models",
                "allow_auto_create",
                "propagate",
                "is_protected",
                "is_matching",
                "expose_metric",
                "expose_datastream",
                "expose_alarm",
            ],
        )

    def get_json_path(self) -> str:
        return quote_safe_path(self.name.strip("*")) + ".json"

    @property
    def scope(self):
        return self.name.rsplit("::", 1)[0] if self.is_scoped else ""

    @property
    def value(self):
        return self.name.split("::")[-1]

    @property
    def badges(self):
        if self.is_builtin:
            return ["fa-ils"]
        return []

    @property
    def is_scoped(self) -> bool:
        """
        Returns True if the label is scoped
        :return:
        """
        return "::" in self.name

    @property
    def is_wildcard(self) -> bool:
        """
        Returns True if the label is wildcard
        :return:
        """
        return self.name.endswith("::*")

    @property
    def is_builtin(self) -> bool:
        """
        Returns True if the label is builtin NOC
        :return:
        """
        return self.name.startswith("noc::")

    @property
    def is_matched(self) -> bool:
        """
        Returns True if the label is matched
        :return:
        """
        return self.name[-1] in MATCH_OPS

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Label"]:
        return Label.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    @classmethod
    def _reset_caches(cls, name):
        try:
            del cls._name_cache[name,]  # Tuple
        except KeyError:
            pass

    @classmethod
    def from_names(self, labels: List[str]) -> List["Label"]:
        """
        Conert list names to Labels list
        """
        r = []
        for ll in labels:
            ll = Label.get_by_name(ll)
            if not ll:
                continue
            r.append(ll)
        return r

    # def __getattr__(self, item):
    #     """
    #     Check enable_XX settings for backward compatible
    #     """
    #     if item in self.ENABLE_MODEL_ID_MAP:
    #         return self.ENABLE_MODEL_ID_MAP[item] in self.allow_models
    #     raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, item))

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        ds_changed = []
        if (not changed_fields and self.expose_metric) or (
            changed_fields and "expose_metric" in changed_fields
        ):
            ds_changed.append("cfgmetricsources")
        if (not changed_fields and self.expose_datastream) or (
            changed_fields and "expose_datastream" in changed_fields
        ):
            ds_changed.append("managedobject")
        if not ds_changed:
            return
        for ds in ds_changed:
            for mo_id in ManagedObject.objects.filter(labels__contains=[self.name]).values_list(
                "id", flat=True
            ):
                yield ds, mo_id

    def clean(self):
        """
        Deny rename Labels
        :return:
        """
        if hasattr(self, "_changed_fields") and "name" in self._changed_fields:
            raise ValueError("Rename label is not allowed operation")
        if hasattr(self, "_changed_fields") and "allow_models" in self._changed_fields:
            am = set(Label.objects.filter(name=self.name).scalar("allow_models").first())
            for model_id in am - set(self.allow_models):
                r = self.check_label(model_id, self.name)
                if r:
                    raise ValueError(f"Referred from model {model_id}: {r!r} (id={r.id})")
        # Wildcard labels are protected
        if not self.is_wildcard and self.is_scoped:
            # Check propagate
            settings = self.effective_settings
            for key, value in settings.items():
                setattr(self, key, value)

    def on_save(self):
        if self.is_scoped and not self.is_wildcard and not self.is_matched:
            self._ensure_wildcards()
        Label._reset_caches(self.name)
        # Check if unset enable and label added to model
        cf = getattr(self, "_changed_fields", None) or {}
        if not cf or "match_regex" in cf or "is_matching" in cf:
            self._refresh_regex_labels()
        if not cf or "match_prefixfilter" in cf or "is_matching" in cf:
            self._refresh_prefixfilter_labels()
        # Propagate Wildcard Settings
        if self.is_wildcard and self.propagate:
            settings = self.effective_settings
            if not settings:
                # Nothing propagate
                return
            coll = Label._get_collection()
            coll.update_many({"name": re.compile(f"{self.scope}::[^*].+")}, {"$set": settings})

    def on_delete(self):
        """

        :return:
        """
        if self.is_wildcard and Label.objects.filter(name__startswith=self.name[:-1]).first():
            raise ValueError("Cannot delete wildcard label with matched labels")
        if self.is_builtin and not self.is_matched:
            raise ValueError("Cannot delete builtin label")

    @classmethod
    def check_label(cls, model, label_name):
        model_ins = get_model(model)
        if is_document(model_ins):
            label = label_name
        else:
            label = [label_name]
        return model_ins.objects.filter(**{"labels__contains": label}).first()

    @staticmethod
    def get_wildcards(label: str) -> List[str]:
        return [
            f"{ll}::*" for ll in accumulate(label.split("::")[:-1], lambda acc, x: f"{acc}::{x}")
        ]

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_setting_cache"), lock=lambda _: allow_model_lock)
    def has_model(cls, label: str, model_id: str) -> bool:
        coll = cls._get_collection()
        wildcards = cls.get_wildcards(label)
        return bool(
            next(
                coll.find(
                    {
                        "name": {"$in": [label] + wildcards},
                        "allow_models": model_id,
                    },
                    {},
                ),
                None,
            )
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_setting_cache"), lock=lambda _: setting_lock)
    def get_effective_setting(cls, label: str, setting: str) -> bool:
        """
        # has_effective_settings
        """
        wildcards = cls.get_wildcards(label)
        coll = cls._get_collection()
        if setting in cls.ENABLE_MODEL_ID_MAP:
            # for backward compatible
            return cls.has_model(label, cls.ENABLE_MODEL_ID_MAP[setting])
        r = next(
            coll.aggregate(
                [
                    {"$match": {"name": {"$in": [label] + wildcards}}},
                    {"$group": {"_id": None, setting: {"$max": f"${setting}"}}},
                ]
            ),
            {},
        )
        return bool(r.get(setting))

    @classmethod
    def get_effective_settings(cls, label: str, include_current: bool = False) -> Dict[str, Any]:
        """
        Returns dict with effective settings
        :param label: Checked label name
        :param include_current: Include current label settings
        """
        # es = {ff: False for ff in cls._fields if ff[:2] in {"en", "bg", "fg"}}
        wildcards = cls.get_wildcards(label)
        if "noc::*" in wildcards:
            wildcards.remove("noc::*")
        if include_current:
            wildcards += [label]
        coll = cls._get_collection()
        match = {"$match": {"name": {"$in": wildcards}, "propagate": True}}
        # if include_current:
        #     match["$match"]["propagate"] = False
        r = next(
            coll.aggregate(
                [
                    match,
                    {"$sort": {"name": 1}},
                    {
                        "$project": {
                            ff: {
                                "$cond": {
                                    "if": {"$eq": [None, f"${ff}"]},
                                    "then": "$$REMOVE",
                                    "else": f"${ff}",
                                }
                            }
                            for ff in cls._fields
                            if ff[:2] in {"al", "ex", "bg", "fg"} or ff == "is_protected"
                        }
                    },
                    {"$group": {"_id": None, "settings": {"$mergeObjects": "$$ROOT"}}},
                ]
            ),
            {"settings": {"_id": None}},
        )
        del r["settings"]["_id"]
        # es.update(r["settings"])
        return r["settings"]

    @property
    def effective_settings(self):
        """
        Returns dict with effective settings
        """
        return Label.get_effective_settings(self.name)

    @classmethod
    def merge_labels(
        cls, iter_labels: Iterable[List[str]], add_wildcard: bool = False
    ) -> List[str]:
        """
        Merge sets of labels, processing the scopes.

        :param iter_labels: Iterator yielding lists of labels
        :param add_wildcard: Add wildcard scope label
        :return:
        """
        seen_scopes: Set[str] = set()
        seen: Set[str] = set()
        r: List[str] = []
        for labels in iter_labels:
            for label in labels:
                if label in seen:
                    continue
                elif "::" in label and label[-1] not in MATCH_OPS:
                    scope = label.rsplit("::", 1)[0]
                    if scope in seen_scopes:
                        continue
                    seen_scopes.add(scope)
                    wildcard = f"{scope}::*"
                    if add_wildcard and wildcard not in seen and scope != "noc":
                        r.append(wildcard)
                        seen.add(wildcard)
                r.append(label)
                seen.add(label)
        return r

    def iter_scopes(self) -> Iterable[str]:
        """
        Yields all scopes
        :return:
        """
        r = []
        for p in self.name.split("::")[:-1]:
            r.append(p)
            yield "::".join(r)

    @classmethod
    def ensure_label(
        cls,
        name,
        model_ids: List[str],
        description=None,
        is_protected=False,
        bg_color1=0xFFFFFF,
        fg_color1=0x000000,
        bg_color2=0xFFFFFF,
        fg_color2=0x000000,
        expose_metric=False,
        expose_datastream=False,
    ) -> None:
        """
        Ensure label is exists, create when necessary
        :param name:
        :param description:
        :param is_protected:
        :param model_ids:
        :param bg_color1:
        :param fg_color1:
        :param bg_color2:
        :param fg_color2:
        :param expose_metric:
        :param expose_datastream:
        :return:
        """
        # if Label.objects.filter(name=name).first():  # Do not use get_by_name. Cached None !
        #     return  # Exists
        label = Label.get_by_name(name)
        if label:
            return  # Exists
        logger.info("[%s] Create label by ensure", name)
        settings = cls.get_effective_settings(name, include_current=True)
        if not settings.get("allow_auto_create"):
            logger.warning("[%s] Not allowed autocreate label", name)
            return
        settings["name"] = name
        settings["description"] = description or "Auto-created"
        settings["is_protected"] = settings.get("is_protected") or is_protected
        settings["allow_models"] = list(set(model_ids) | set(settings["allow_models"] or []))
        settings["is_autogenerated"] = True
        if bg_color1 and bg_color1 != 0xFFFFFF:
            settings["bg_color1"] = bg_color1
        if fg_color1:
            settings["fg_color1"] = fg_color1
        if bg_color2 and bg_color2 != 0xFFFFFF:
            settings["bg_color2"] = bg_color2
        if fg_color2:
            settings["fg_color2"] = fg_color2
        if expose_metric:
            settings["expose_metric"] = expose_metric
        if expose_datastream:
            settings["expose_datastream"] = expose_datastream
        Label(**settings).save()

    @classmethod
    def ensure_labels(
        cls,
        labels: List[str],
        model_ids: List[str],
    ) -> List[str]:
        """
        Yields all scopes
        :return:
        """
        for ll in labels:
            cls.ensure_label(
                name=ll,
                model_ids=model_ids,
                is_protected=False,
            )
        return labels

    def _ensure_wildcards(self):
        """
        Create all necessary wildcards for a scoped labels
        :return:
        """
        for scope in self.iter_scopes():
            # Ensure wildcard
            Label.ensure_label(
                f"{scope}::*",
                [],
                description=f"Wildcard label for scope {scope}",
                is_protected=False,
                bg_color1=self.bg_color1,
                fg_color1=self.fg_color1,
                bg_color2=self.bg_color2,
                fg_color2=self.fg_color2,
            )

    def get_matched_labels(self) -> List[str]:
        """
        Get list of matched labels for wildcard label
        :return:
        """
        label = self.name
        if label.endswith("::*"):
            return [
                x.name
                for x in Label.objects.filter(name__startswith=label[:-1]).only("name")
                if not x.name.endswith("::*")
            ]
        return [label]

    def get_match_regex_rules(self) -> Dict[Tuple[str, str], List[str]]:
        """
        Yields all scopes
        :return:
        """
        r = defaultdict(list)  # model, field -> Regex List
        for ri in self.match_regex:
            if ri.scope not in REGEX_LABEL_SCOPES:
                # Unknown scope
                continue
            r[REGEX_LABEL_SCOPES[ri.scope]] += [ri.regexp]
        return r

    def _refresh_prefixfilter_labels(self):
        """
        Recalculate labels on model
        :return:
        """
        c_map = {"all": " AND ", "any": " OR "}
        logger.info("[%s] Refresh Prefix Filter", self.name)
        if "sa.ManagedObject" in self.allow_models:
            Label.remove_model_labels("sa.ManagedObject", [self.name])
        if not self.is_matching:
            return
        for rule in self.match_prefixfilter:
            model_id, field = PREFIXFILTER_LABEL_SCOPES[rule.scope]
            if model_id not in self.allow_models:
                continue
            model = get_model(model_id)
            prefixes = [
                str(p)
                for p in PrefixTablePrefix.objects.filter(table=rule.prefix_table.id).values_list(
                    "prefix", flat=True
                )
            ]
            if is_document(model):
                ...
            else:
                condition = c_map[rule.condition].join(
                    [f"cast_test_to_inet({field}) <<= %s"] * len(prefixes)
                )
                params = [[self.name]] + prefixes
                sql = f"""
                UPDATE {model._meta.db_table}
                SET effective_labels=ARRAY (
                SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
                )
                WHERE {condition}
                """
                with pg_connection.cursor() as cursor:
                    cursor.execute(sql, params)

    def _refresh_regex_labels(self):
        """
        Recalculate labels on model
        :return:
        """
        r = self.get_match_regex_rules()
        for model_id in set(mid for mid, _ in r):
            # Skipping interface for poor performance for $pull operation
            # For 60 second over 12 million
            if model_id != "inv.Interface":
                # Cleanup current labels
                # logger.info("[%s] Cleanup Interface effective labels: %s", self.name, self.name)
                Label.remove_model_labels(model_id, [self.name])
        regxs = defaultdict(list)
        for model_id, field in r:
            if model_id not in self.allow_models:
                continue
            model = get_model(model_id)
            regxs[model] += [(field, r[(model_id, field)])]

        for model in regxs:
            if is_document(model):
                # Apply new rule
                coll = model._get_collection()
                coll.bulk_write(
                    [
                        UpdateMany(
                            {
                                "$or": [
                                    {field: {"$in": [re.compile(x) for x in rxs]}}
                                    for field, rxs in regxs[model]
                                ]
                            },
                            {"$addToSet": {"effective_labels": self.name}},
                        )
                    ]
                )
            else:
                # Apply new rule
                params = [[self.name]]
                conditions = []
                for field, rxs in regxs[model]:
                    params += rxs
                    conditions += [f"{field} ~ %s"] * len(rxs)
                condition = " OR ".join(conditions)
                sql = f"""
                UPDATE {model._meta.db_table}
                SET effective_labels=ARRAY (
                SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
                )
                WHERE {condition}
                """
                with pg_connection.cursor() as cursor:
                    cursor.execute(sql, params)

    @classmethod
    def build_effective_labels(cls, instance, sender=None) -> Set[str]:
        """Build Effective labels for Instance"""

        def default_iter_effective_labels(instance) -> Iterable[List[str]]:
            yield instance.labels or []

        if not instance._has_effective_labels:
            return set(instance.labels)
        model_id = get_model_id(instance)
        sender = sender or get_model(model_id)
        # Check Match labels
        match_labels = set()
        for ml in getattr(instance, "match_rules", []):
            if is_document(instance):
                match_labels |= set(ml.labels or [])
            else:
                match_labels |= set(ml.get("labels", []))
        # Validate instance labels
        can_set_label = getattr(
            sender,
            "can_set_label",
            partial(cls.has_model, model_id=model_id),
        )
        for label in set(instance.labels):
            if not can_set_label(label):
                # Check can_set_label method
                raise ValueError(f"Invalid label: {label}")
            if label in match_labels:
                raise ValueError(
                    f"Label on MatchRules and Label at the same time is not allowed: {label}"
                )
        # Build and clean up effective labels. Filter can_set_labels
        labels_iter = getattr(sender, "iter_effective_labels", default_iter_effective_labels)
        el = {
            ll
            for ll in Label.merge_labels(labels_iter(instance), add_wildcard=True)
            if ll[-1] in MATCH_OPS or can_set_label(ll) or ll[-1] == "*"
        }
        return el

    @classmethod
    def model(cls, m_cls):
        """
        Decorator to denote models with labels.
        Contains field validation and `effective_labels` generation.

        Usage:
        ```
        @Label.model
        class MyModel(...)
        ```

        Adds pre-save hook to check and process `.labels` fields. Raises ValueError
        if any of the labels is not exists.

        Target model may have `iter_effective_labels` method with following signature:
        ```
        def iter_effective_labels(self) -> Iterable[List[str]]
        ```
        which may yield a list of effective labels from related objects to form
        `effective_labels` field.

        :param m_cls: Target model class
        :return:
        """

        def on_pre_save(sender, instance=None, document=None, *args, **kwargs):
            instance = instance or document
            # Clean up labels
            labels = Label.merge_labels([instance.labels or []])
            instance.labels = labels
            # Block effective labels
            if instance._has_effective_labels:
                el = Label.build_effective_labels(instance, sender)
                # Build and clean up effective labels. Filter can_set_labels
                if not instance.effective_labels or el != set(instance.effective_labels):
                    instance.effective_labels = list(sorted(el))
            if instance._has_lazy_labels and instance.name != instance._last_name:
                for label in Label.objects.filter(
                    name=re.compile(f"noc::.+::{instance._last_name}::[{''.join(MATCH_OPS)}]")
                ):
                    label.delete()

        def on_post_init_set_name(sender, instance=None, document=None, *args, **kwargs):
            # For rename detect
            instance = instance or document
            instance._last_name = instance.name

        m_cls._has_lazy_labels = hasattr(m_cls, "iter_lazy_labels")
        m_cls._has_effective_labels = hasattr(m_cls, "effective_labels")

        # Install handlers
        if is_document(m_cls):
            from mongoengine import signals as mongo_signals

            mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
            if m_cls._has_lazy_labels:
                mongo_signals.post_init.connect(on_post_init_set_name, sender=m_cls, weak=False)
        else:
            from django.db.models import signals as django_signals

            django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
            if m_cls._has_lazy_labels:
                django_signals.post_init.connect(on_post_init_set_name, sender=m_cls, weak=False)
        return m_cls

    @classmethod
    def match_labels(
        cls, category, allowed_op: Set = None, matched_scopes: Set = None, parent_op: Set = None
    ):
        """
        Decorator to denote models with labels.
        Ensure wildcard and contains labels

        Usage:
        ```
        @Label.match_labels
        class MyModel(...)
        ```

        Adds pre-save hook to ensure match labels:
        * noc::<category>::<instance.name>::= - full match
        * noc::<category>::<instance.name>::> - full contains in instance set
        * noc::<category>::<instance.name>::< - full contains instance set
        * noc::<category>::<instance.name>::& - interception
        """

        def on_post_save(
            sender,
            instance=None,
            document=None,
            category=category,
            allowed_op=allowed_op,
            matched_scopes=matched_scopes,
            parent_op=parent_op,
            *args,
            **kwargs,
        ):
            instance = instance or document
            matched_scopes = matched_scopes or {""}
            # Ensure matches
            ops = MATCH_OPS
            if allowed_op:
                ops = MATCH_OPS.intersection(allowed_op)
            for op in ops:
                for matched_scope in matched_scopes:
                    if matched_scope:
                        matched_scope += "::"
                    if parent_op and getattr(instance, "parent", None):
                        for pop in parent_op:
                            Label.ensure_label(
                                f"noc::{category}::{instance.parent.name}::{matched_scope}{pop}",
                                [get_model_id(instance)],
                                is_protected=False,
                            )
                    Label.ensure_label(
                        f"noc::{category}::{instance.name}::{matched_scope}{op}",
                        [get_model_id(instance)],
                        is_protected=False,
                    )

        def inner(m_cls):
            # Install handlers
            if is_document(m_cls):
                from mongoengine import signals as mongo_signals

                mongo_signals.post_save.connect(on_post_save, sender=m_cls, weak=False)
            else:
                from django.db.models import signals as django_signals

                django_signals.post_save.connect(on_post_save, sender=m_cls, weak=False)

            return m_cls

        return inner

    @classmethod
    def _change_model_labels(
        cls,
        model_id: str,
        add_labels: List[str] = None,
        remove_labels: List[str] = None,
        instance_filters: Optional[List[Tuple[str, Any]]] = None,
        effective_only: bool = True,
    ):
        """
        Change model labels field with DB query
        if set add_labels - append this labels to effective_labels field for instances settings by filter_ids
        If set remove_labels - remove labels from effective_labels field where set that
        if set both - replace remove_labels to add_labels for instances where set remove_labels
        If not set both - set effective_labels to empty array

        :param model_id: Model ID
        :param add_labels: Labels for add to effective_labels
        :param remove_labels: Labels for remove from effective_labels
        :param instance_filters:
        :param effective_only: Apply only effective labels field
        :return:
        """
        model = get_model(model_id)
        if not hasattr(model, "effective_labels"):
            # Model has not supported labels
            return

        params, conditions, query_set = [], [], ""
        if add_labels and not remove_labels:
            # SET effective_labels=ARRAY (SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e))
            params += [add_labels]
            query_set = "(SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e))"
        elif remove_labels and not add_labels:
            # SET effective_labels=ARRAY (SELECT unnest(effective_labels) EXCEPT SELECT unnest(%s::varchar[])
            params += [remove_labels, remove_labels]
            query_set = "(SELECT unnest(effective_labels) EXCEPT SELECT unnest(%s::varchar[]))"
            conditions += [" effective_labels && %s::varchar[] "]
        elif remove_labels and add_labels:
            params += [add_labels, remove_labels]
            query_set = "(SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e) EXCEPT SELECT unnest(%s::varchar[]))"
            if not instance_filters:
                conditions += [" effective_labels && %s::varchar[] "]
        # Construct condition
        # Where str,int - WHERE {field} ~ %s
        # Where List[str] - id = ANY (%s::varchar[])
        # Where List[int] - id = ANY (%s::numeric[])
        for field, ids in instance_filters or []:
            if isinstance(ids, list) and isinstance(ids[0], int):
                conditions += [f" {field} = ANY (%s::numeric[])"]
            elif isinstance(ids, list):
                conditions += [f" {field} = ANY (%s::text[])"]
                ids = [str(x) for x in ids]
            else:
                conditions += [f" {field} = %s"]
            params += [ids]
        # Construct query
        sql = f"""
        UPDATE {model._meta.db_table}
        SET effective_labels=ARRAY {query_set if query_set else " []::varchar[] "}
        """
        if conditions:
            sql += f" WHERE {' AND '.join(conditions)} "
        with pg_connection.cursor() as cursor:
            cursor.execute(sql, params)

    @classmethod
    def _change_document_labels(
        cls,
        model_id: str,
        add_labels: List[str] = None,
        remove_labels: List[str] = None,
        instance_filters: Optional[List[Tuple[str, Any]]] = None,
        effective_only: bool = True,
    ):
        """
        Change model labels field with DB query
        if set add_labels - append this labels to effective_labels field for instances settings by filter_ids
        If set remove_labels - remove labels from effective_labels field where set that
        if set both - replace remove_labels to add_labels for instances where set remove_labels
        If not set both - set effective_labels to empty array

        :param model_id: Model ID
        :param add_labels: Labels for add to effective_labels
        :param remove_labels: Labels for remove from effective_labels
        :param instance_filters:
        :param effective_only: Apply only effective labels field
        :return:
        """
        model = get_model(model_id)
        if not hasattr(model, "effective_labels"):
            # Model has not supported labels
            return
        # Construct match
        match, q_set = {}, {}
        if add_labels:
            # {"$addToSet": {"effective_labels": {"$each": add_labels}}}
            q_set["$addToSet"] = {"effective_labels": {"$each": add_labels}}
        if remove_labels:
            q_set["$pull"] = {"effective_labels": {"$in": remove_labels}}
            match["effective_labels"] = {"$in": remove_labels}
        for field, ids in instance_filters or []:
            if isinstance(ids, list):
                match[field] = {"$in": ids}
            else:
                match[field] = ids
        # Add labels ? bulk
        coll = model._get_collection()
        coll.bulk_write([UpdateMany(match, q_set)])

    @classmethod
    def add_model_labels(
        cls,
        model_id: str,
        labels: List[str],
        instance_filters: Optional[List[Tuple[str, Any]]] = None,
    ):
        """
        Add Labels on models effective_labels field
        :param model_id: Model ID
        :param labels: Labels for remove from effective_labels
        :param instance_filters: Model instance filters list
        :return:
        """
        model = get_model(model_id)
        if is_document(model):
            cls._change_document_labels(model_id, labels, instance_filters=instance_filters)
        else:
            cls._change_model_labels(model_id, labels, instance_filters=instance_filters)

    @classmethod
    def remove_model_labels(
        cls,
        model_id: str,
        labels: List[str],
        instance_filters: Optional[List[Tuple[str, Any]]] = None,
    ):
        """
        Remove labels from effective_labels field on models
        :param model_id: Model ID
        :param labels: Labels for remove from effective_labels
        :param instance_filters: Model instance filters list
        :return:
        """
        model = get_model(model_id)
        if is_document(model):
            cls._change_document_labels(
                model_id, remove_labels=labels, instance_filters=instance_filters
            )
        else:
            cls._change_model_labels(
                model_id, remove_labels=labels, instance_filters=instance_filters
            )

    @staticmethod
    def get_instance_profile(
        profile_model,
        labels: List[str],
        **kwargs,
    ) -> Optional[str]:
        """
        Return Profile ID for labels if it support Labels Classification
        :param profile_model:
        :param labels: Labels for profile classification
        :param kwargs:
        :return:
        """
        # effective_labels = labels or Label.merge_labels(instance.iter_effective_labels(instance))
        logger.debug("[%s] Getting profile by labels: %s", str(profile_model), labels)
        if is_document(profile_model):
            coll = profile_model._get_collection()
            pipeline = [
                {
                    "$match": {
                        "match_rules": {
                            "$elemMatch": {
                                "dynamic_order": {"$ne": 0},
                                "labels": {"$in": labels},
                            }
                        }
                    }
                },
                {"$unwind": "$match_rules"},
                {
                    "$project": {
                        "dynamic_order": "$match_rules.dynamic_order",
                        "labels": "$match_rules.labels",
                        "diff": {"$setDifference": ["$match_rules.labels", labels]},
                        "handlers": 1,
                    }
                },
                {"$match": {"diff": [], "dynamic_order": {"$ne": 0}}},
                {"$sort": {"dynamic_order": 1}},
            ]
            match_profiles = coll.aggregate(pipeline)
        else:
            with pg_connection.cursor() as cursor:
                query = f"""
                                    SELECT pt.id, t.labels, t.dynamic_order, t.handler, match_rules
                                    FROM {profile_model._meta.db_table} as pt
                                    CROSS JOIN LATERAL jsonb_to_recordset(pt.match_rules::jsonb)
                                    AS t("dynamic_order" int, "labels" jsonb, "handler" text)
                                    WHERE t.labels ?| %s::varchar[] order by dynamic_order
                                """
                cursor.execute(query, [labels])
                match_profiles = [
                    {
                        "_id": r[0],
                        "labels": orjson.loads(r[1]),
                        "dynamic_order": r[2],
                        "handler": r[3],
                    }
                    for r in cursor.fetchall()
                ]
        sef = set(labels)
        for profile in match_profiles:
            if "handler" in profile and profile["handler"]:
                handler = Handler.get_by_id(profile["handler"])
                handler = handler.get_handler()
                if handler(labels):
                    return profile["_id"]
            if not set(profile["labels"]) - sef:
                return profile["_id"]

    @classmethod
    def dynamic_classification(
        cls,
        profile_model_id: str,
        profile_field: str = "profile",
        sync_profile: bool = True,
        sync_labels: bool = True,
    ):
        """
        :param profile_model_id: Profile Model, that assigned
        :param profile_field: Model profile field
        :param sync_profile: Assigned profile by match rules
        :param sync_labels: Expose profile labels to reference instances
        """

        def on_pre_save(
            sender,
            instance=None,
            document=None,
            profile_model_id=profile_model_id,
            profile_field=profile_field,
            *args,
            **kwargs,
        ):
            """

            :param sender:
            :param instance:
            :param document:
            :param profile_model_id:
            :param profile_field:
            :param args:
            :param kwargs:
            :return:
            """
            profile_model = get_model(profile_model_id)
            if not hasattr(profile_model, "match_rules"):
                # Dynamic classification not suported
                return
            instance = instance or document
            policy = getattr(instance, "get_dynamic_classification_policy", None)
            if policy and policy() == "D":
                # Dynamic classification not enabled
                return
            profile_field = profile_field or "profile"
            if not hasattr(instance, "effective_labels"):
                # Instance without effective labels
                return
            profile_id = cls.get_instance_profile(
                profile_model, Label.merge_labels(instance.iter_effective_labels(instance))
            )
            if profile_id and instance.profile.id != profile_id:
                profile = profile_model.get_by_id(profile_id)
                setattr(instance, profile_field, profile)

        def on_profile_post_save(
            sender,
            instance=None,
            document=None,
            instance_model_id=None,
            profile_field=profile_field,
            *args,
            **kwargs,
        ):
            instance = instance or document
            if document:
                changed_fields = getattr(document, "_changed_fields", None)
            else:
                changed_fields = getattr(instance, "changed_fields", None)
            if (not changed_fields or "labels" in changed_fields) and instance.labels:
                Label.add_model_labels(
                    instance_model_id,
                    labels=instance.labels,
                    instance_filters=[(f"{profile_field}_id", instance.id)],
                )
            if "match_rules" in changed_fields and not document:
                Label.sync_model_profile(
                    instance_model_id, profile_model_id, profile_field=profile_field
                )

        def inner(m_cls):
            # Install profile set handlers
            if is_document(m_cls):
                from mongoengine import signals as mongo_signals

                if sync_profile:
                    # Profile set handlers
                    mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
                if sync_labels:
                    mongo_signals.post_save.connect(
                        partial(on_profile_post_save, instance_model_id=get_model_id(m_cls)),
                        sender=get_model(profile_model_id),
                        weak=False,
                    )
            else:
                from django.db.models import signals as django_signals

                if sync_profile:
                    # Profile set handlers
                    django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
                if sync_labels:
                    django_signals.post_save.connect(
                        partial(on_profile_post_save, instance_model_id=get_model_id(m_cls)),
                        sender=get_model(profile_model_id),
                        weak=False,
                    )
            # Install Profile Labels expose
            return m_cls

        return inner

    @classmethod
    def filter_labels(cls, labels: List[str], pred: Callable) -> List[str]:
        """
        Filter labels satisfying predicate
        :param labels:
        :param pred:
        :return:
        """
        if not labels:
            return []
        return [label.name for label in Label.objects.filter(name__in=labels) if pred(label)]

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_rx_cache"),
        key=lambda c, ri: getattr(ri, "regexp", None),
        lock=lambda _: re_lock,
    )
    def _get_re(cls, rxi: "RegexItem") -> Optional[re.Pattern]:
        flags = 0
        if rxi.flag_multiline:
            flags |= re.MULTILINE
        if rxi.flag_dotall:
            flags |= re.DOTALL
        try:
            rx = re.compile(rxi.regexp, flags=flags)
        except re.error:
            return None
        return rx

    @classmethod
    def get_effective_regex_labels(cls, scope: str, value: str) -> List[str]:
        """
        :param: scope - check `enable_<scope>` for filter enable regex
        :param: value - string value for check
        """
        labels = []
        for rx, label in cls.get_regex_labels(scope):
            if rx.match(value):
                labels += [label]
        return labels

    @classmethod
    def get_effective_prefixfilter_labels(cls, scope: str, value: str) -> List[str]:
        """

        :param scope:
        :param value:
        :return:
        """
        mq = m_Q()
        for pt, condition in PrefixTable.iter_match_prefix(value):
            # condition = "any" if condition != "=" else "all"
            mq |= m_Q(
                match_prefixfilter__match={
                    "scope": scope,
                    "prefix_table": pt.id,
                    "condition": {"$in": ["any", "all"]},
                }
            )
        if not mq:
            return []
        return list(Label.objects.filter(mq).values_list("name"))

    @classmethod
    def get_effective_vlanfilter_labels(cls, scope: str, value: Union[int, List[int]]) -> List[str]:
        """

        :param scope:
        :param value:
        :return:
        """
        mq = m_Q()
        for vf, condition in VLANFilter.iter_match_vlanfilter(value):
            condition = "any" if condition != "=" else "all"
            mq |= m_Q(
                match_vlanfilter__match={
                    "scope": scope,
                    "vlan_filter": vf.id,
                    "condition": condition,
                }
            )
        if not mq:
            return []
        return list(Label.objects.filter(mq).values_list("name"))

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rx_labels_cache"), lock=lambda _: rx_labels_lock)
    def get_regex_labels(cls, scope: str) -> Tuple[re.Pattern, str]:
        """
        :param: scope - check `enable_<scope>` for filter enable regex
        """
        rxs = []
        for ll in Label.objects.filter(
            __raw__={"is_matching": True, "match_regex": {"$elemMatch": {"scope": scope}}}
        ):
            for rx in ll.match_regex:
                if rx.scope == scope:
                    rx = cls._get_re(rx)
                    if not rx:
                        continue
                    rxs += [(rx, ll.name)]
        return tuple(rxs)

    @classmethod
    def sync_model_profile(
        cls,
        model_id: str,
        model_profile_id: str,
        profile_field="profile",
        query_filter: Optional[List[Tuple[str, str]]] = None,
    ):
        """
        Update profile by match rule
        :param model_id:
        :param model_profile_id: Profile model
        :param profile_field: Field name for profile assigned
        :param query_filter: Optional filter by list (field, value)
        :return:
        """
        model = get_model(model_id)
        if not model:
            return
        table = model._meta.db_table
        profile = get_model(model_profile_id)
        # Build filter
        where, params = [], []
        for field, ids in query_filter or []:
            if isinstance(ids, list) and isinstance(ids[0], int):
                where += [f"{field} = ANY (%s::numeric[])"]
            elif isinstance(ids, list):
                where += [f"{field} = ANY (%s::text[])"]
            else:
                where += [f"{field} = %s"]
            params += [ids]
        where = ("WHERE " + " AND ".join(where)) if where else ""
        if not is_document(profile):
            profile_field = f"{profile_field}_id"
        # Build query
        SQL = f"""
            UPDATE {table} AS update_t SET {profile_field} = sq.erg[1]
             FROM (SELECT t.id as id, t.effective_labels, array_remove(array_agg(mrs.prof ORDER BY mrs.d_order), NULL) AS erg FROM {table} AS t
             LEFT JOIN (select * from jsonb_to_recordset(%s::jsonb) AS x(prof int, ml text[], d_order int)) AS mrs
             ON t.effective_labels::text[] @> mrs.ml {where} GROUP BY t.id
             HAVING array_length(array_remove(array_agg(mrs.prof ORDER BY mrs.d_order), NULL), 1) is not NULL) AS sq
            WHERE sq.id = update_t.id and {profile_field} != sq.erg[1]
            """
        r = []
        for p_id, mrs in profile.objects.filter().values_list("id", "match_rules"):
            for rule in mrs:
                if not rule["dynamic_order"]:
                    continue
                r += [{"prof": p_id, "ml": list(rule["labels"]), "d_order": rule["dynamic_order"]}]
        params = [orjson.dumps(r).decode("utf-8")] + params
        with pg_connection.cursor() as cursor:
            cursor.execute(SQL, params)

    @classmethod
    def iter_model_profile(
        cls,
        model_id: str,
        model_profile_id: str,
        query_filter: Optional[List[Tuple[str, str]]] = None,
    ) -> Tuple[str, str, Optional[str]]:
        """
        Sync profile by match rule
        :param model_id: Instance model_id
        :param model_profile_id: Profile model
        :param query_filter: Optional filter by list (field, value)
        :return:
        """
        model = get_model(model_id)
        if not model:
            return
        table = model._meta.db_table
        profile = get_model(model_profile_id)
        # Build filter
        where, params = [], []
        for field, ids in query_filter or []:
            if isinstance(ids, list) and isinstance(ids[0], int):
                where += [f"{field} = ANY (%s::numeric[])"]
            elif isinstance(ids, list):
                where += [f"{field} = ANY (%s::text[])"]
            else:
                where += [f"{field} = %s"]
            params += [ids]
        where = ("WHERE " + " AND ".join(where)) if where else ""
        # Build query
        SQL = f"""
             SELECT t.id as id, (array_agg(mrs.prof ORDER BY mrs.d_order))[1] AS erg FROM {table} AS t
             LEFT JOIN (select * from jsonb_to_recordset(%s::jsonb) AS x(prof int, ml text[], d_order int)) AS mrs
             ON t.effective_labels::text[] @> mrs.ml {where} GROUP BY t.id
             HAVING  array_length(array_remove(array_agg(mrs.prof ORDER BY mrs.d_order), NULL), 1) is not NULL
            """
        r = []
        for p_id, mrs in profile.objects.filter().values_list("id", "match_rules"):
            for rule in mrs:
                if not rule["dynamic_order"]:
                    continue
                r += [{"prof": p_id, "ml": list(rule["labels"]), "d_order": rule["dynamic_order"]}]
        params = [orjson.dumps(r).decode("utf-8")] + params
        with pg_connection.cursor() as cursor:
            cursor.execute(SQL, params)
            yield from cursor

    @classmethod
    def iter_document_profile(
        cls,
        model_id: str,
        model_profile_id: str,
        query_filter: Optional[List[Tuple[str, str]]] = None,
    ) -> Tuple[str, str, Optional[str]]:
        """
        Iterate over instance profile
        :param model_id: Instance model_id
        :param model_profile_id: Profile model
        :param query_filter: Optional filter by list (field, value)
        """
        model = get_model(model_id)
        if not model:
            return
        pipeline = []
        match = {}
        for field, ids in query_filter or []:
            if isinstance(ids, list):
                match[f"{field}"] = {"$in": ids}
            else:
                match[field] = ids
        if match:
            pipeline += [{"$match": match}]
        profile_model = get_model(model_profile_id)
        profile_coll = profile_model._get_collection_name()
        pipeline += [
            {
                "$lookup": {
                    "from": profile_coll,
                    "let": {"el": "$effective_labels"},
                    "pipeline": [
                        {"$unwind": "$match_rules"},
                        {"$match": {"$expr": {"$setIsSubset": ["$match_rules.labels", "$$el"]}}},
                        {"$sort": {"match_rules.dynamic_order": 1}},
                    ],
                    "as": "profiles",
                }
            },
            {"$project": {"_id": 1, "name": 1, "p_ids": "$profiles._id"}},
        ]
        coll = model._get_collection()
        for row in coll.aggregate(pipeline):
            yield row["_id"], row.get("name"), row["p_ids"][0] if row["p_ids"] else None
