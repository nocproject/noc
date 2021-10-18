# ----------------------------------------------------------------------
# Label model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import re
from typing import Optional, List, Set, Iterable, Dict, Any, Callable, Tuple
from threading import Lock
from collections import defaultdict
from itertools import accumulate

# Third-party modules
from pymongo import UpdateMany
from mongoengine.document import Document, EmbeddedDocument
from django.db import connection
from mongoengine.fields import (
    StringField,
    IntField,
    BooleanField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
)
import cachetools
import orjson

# NOC modules
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.handler import Handler
from noc.main.models.remotesystem import RemoteSystem
from noc.models import get_model, is_document, LABEL_MODELS


MATCH_OPS = {"=", "<", ">", "&"}

MATCH_BADGES = {
    "=": "=",
    "<": "fa-chevron-left",
    ">": "fa-chevron-right",
    "&": "&",
}

REGEX_LABELS_SCOPES = {
    "managedobject_name": ("sa.ManagedObject", "name"),
    "managedobject_address": ("sa.ManagedObject", "address"),
    "managedobject_description": ("sa.ManagedObject", "description"),
    "interface_name": ("inv.Interface", "name"),
    "interface_description": ("inv.Interface", "description"),
    "sensor_local_id": ("inv.Sensor", "local_id"),
}

id_lock = Lock()
re_lock = Lock()
rx_labels_lock = Lock()


class RegexItem(EmbeddedDocument):
    regexp = StringField(required=True)
    regexp_compiled = StringField(required=False)
    # Set Multiline flag
    flag_multiline = BooleanField(default=False)
    # Set DotAll flag
    flag_dotall = BooleanField(default=False)
    scope = StringField(choices=list(REGEX_LABELS_SCOPES), required=True)

    def __str__(self):
        return f'{self.scope}: {self.regexp}, {"MULTI" if self.flag_multiline else ""}|{"DOTALL" if self.flag_dotall else ""}'


@on_save
@on_delete
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
        "indexes": [
            ("is_regex", "match_regex.scope")
        ],
    }

    name = StringField(unique=True)
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
    is_regex = BooleanField(default=False)
    # For scoped - to propagating settings on own labels
    propagate = BooleanField(default=False)
    # Label scope
    enable_agent = BooleanField(default=False)
    enable_service = BooleanField(default=False)
    enable_serviceprofile = BooleanField(default=False)
    enable_managedobject = BooleanField(default=False)
    enable_managedobjectprofile = BooleanField(default=False)
    enable_administrativedomain = BooleanField(default=False)
    enable_authprofile = BooleanField(default=False)
    enable_commandsnippet = BooleanField(default=False)
    #
    enable_allocationgroup = BooleanField(default=False)
    enable_networksegment = BooleanField(default=False)
    enable_object = BooleanField(default=False)
    enable_objectmodel = BooleanField(default=False)
    enable_platform = BooleanField(default=False)
    enable_resourcegroup = BooleanField(default=False)
    enable_sensor = BooleanField(default=False)
    enable_sensorprofile = BooleanField(default=False)
    enable_interface = BooleanField(default=False)
    #
    enable_subscriber = BooleanField(default=False)
    enable_subscriberprofile = BooleanField(default=False)
    enable_supplier = BooleanField(default=False)
    enable_supplierprofile = BooleanField(default=False)
    #
    enable_dnszone = BooleanField(default=False)
    enable_dnszonerecord = BooleanField(default=False)
    #
    enable_division = BooleanField(default=False)
    #
    enable_kbentry = BooleanField(default=False)
    # IP
    enable_ipaddress = BooleanField(default=False)
    enable_addressprofile = BooleanField(default=False)
    enable_ipaddressrange = BooleanField(default=False)
    enable_ipprefix = BooleanField(default=False)
    enable_prefixprofile = BooleanField(default=False)
    enable_vrf = BooleanField(default=False)
    enable_vrfgroup = BooleanField(default=False)
    # Peer
    enable_asn = BooleanField(default=False)
    enable_assetpeer = BooleanField(default=False)
    enable_peer = BooleanField(default=False)
    # VC
    enable_vc = BooleanField(default=False)
    enable_vlan = BooleanField(default=False)
    enable_vlanprofile = BooleanField(default=False)
    enable_vpn = BooleanField(default=False)
    enable_vpnprofile = BooleanField(default=False)
    # SLA
    enable_slaprobe = BooleanField(default=False)
    enable_slaprofile = BooleanField(default=False)
    # FM
    enable_alarm = BooleanField(default=False)
    # Enable Workflow State
    enable_workflowstate = BooleanField(default=False)
    # Exposition scope
    expose_metric = BooleanField(default=False)
    expose_datastream = BooleanField(default=False)
    # Regex
    match_regex = ListField(EmbeddedDocumentField(RegexItem))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _setting_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _rx_labels_cache = cachetools.TTLCache(maxsize=20, ttl=120)
    _rx_cache = cachetools.TTLCache(maxsize=100, ttl=600)

    def __str__(self):
        return self.name

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
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    @classmethod
    def _reset_caches(cls, name):
        try:
            del cls._name_cache[
                name,  # Tuple
            ]
        except KeyError:
            pass

    def clean(self):
        """
        Deny rename Labels
        :return:
        """
        if hasattr(self, "_changed_fields") and "name" in self._changed_fields:
            raise ValueError("Rename label is not allowed operation")
        if hasattr(self, "_changed_fields") and self._changed_fields:
            for model_id, setting in LABEL_MODELS.items():
                if setting in self._changed_fields and not getattr(self, setting, None):
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
        if self._created or getattr(self, "_changed_fields", None):
            if self.is_regex:
                self._refresh_regex_labels()
            # Propagate Wildcard Settings
            if self.is_wildcard and self.propagate:
                settings = self.effective_settings
                coll = Label._get_collection()
                coll.update_many({"name": re.compile(f"{self.scope}::[^*].+")}, {"$set": settings})

    def on_delete(self):
        """

        :return:
        """
        if self.is_wildcard and any(Label.objects.filter(name__startswith=self.name[:-1])):
            raise ValueError("Cannot delete wildcard label with matched labels")
        if self.is_builtin and not self.is_matched:
            raise ValueError("Cannot delete builtin label")
        # Check if label added to model
        for model_id, setting in LABEL_MODELS.items():
            if not getattr(self, setting):
                continue
            r = self.check_label(model_id, self.name)
            if r:
                raise ValueError(f"Referred from model {model_id}: {r!r} (id={r.id})")

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
    @cachetools.cachedmethod(operator.attrgetter("_setting_cache"))
    def get_effective_setting(cls, label: str, setting: str) -> bool:
        wildcards = cls.get_wildcards(label)
        coll = cls._get_collection()
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
    def get_effective_settings(cls, label: str, all_settings: bool = False) -> Dict[str, Any]:
        """
        Returns dict with effective settings
        """
        # es = {ff: False for ff in cls._fields if ff[:2] in {"en", "bg", "fg"}}
        wildcards = cls.get_wildcards(label)
        if "noc::*" in wildcards:
            wildcards.remove("noc::*")
        if all_settings:
            wildcards += [label]
        coll = cls._get_collection()
        match = {"$match": {"name": {"$in": wildcards}, "propagate": True}}
        if all_settings:
            match["$match"]["propagate"] = False
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
                            if ff[:2] in {"en", "ex", "bg", "fg"} or ff == "is_protected"
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
    def merge_labels(cls, iter_labels: Iterable[List[str]]) -> List[str]:
        """
        Merge sets of labels, processing the scopes.

        :param iter_labels: Iterator yielding lists of labels
        :return:
        """
        seen_scopes: Set[str] = set()
        seen: Set[str] = set()
        r: List[str] = []
        for labels in iter_labels:
            for label in labels:
                if label in seen:
                    continue
                elif "::" in label and not label[-1] in MATCH_OPS:
                    scope = label.rsplit("::", 1)[0]
                    if scope in seen_scopes:
                        continue
                    seen_scopes.add(scope)
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
        description=None,
        is_protected=False,
        is_autogenerated=False,
        enable_managedobject=False,
        enable_slaprobe=False,
        enable_interface=False,
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
        :param bg_color1:
        :param fg_color1:
        :param bg_color2:
        :param fg_color2:
        :return:
        """
        # if Label.objects.filter(name=name).first():  # Do not use get_by_name. Cached None !
        #     return  # Exists
        label = Label.get_by_name(name)
        if label:
            return  # Exists
        settings = cls.get_effective_settings(name)
        settings["name"] = name
        settings["description"] = description or "Auto-created"
        settings["is_protected"] = settings.get("is_protected") or is_protected
        if is_autogenerated:
            settings["is_autogenerated"] = is_autogenerated
        if enable_managedobject:
            settings["enable_managedobject"] = enable_managedobject
        if enable_slaprobe:
            settings["enable_slaprobe"] = enable_slaprobe
        if enable_interface:
            settings["enable_interface"] = enable_interface
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
        cls, labels: List[str], enable_managedobject=False, enable_interface=False
    ) -> List[str]:
        """
        Yields all scopes
        :return:
        """
        for ll in labels:
            cls.ensure_label(
                name=ll,
                is_autogenerated=True,
                is_protected=False,
                enable_managedobject=enable_managedobject,
                enable_interface=enable_interface,
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
            if ri.scope not in REGEX_LABELS_SCOPES:
                # Unknown scope
                continue
            r[REGEX_LABELS_SCOPES[ri.scope]] += [ri.regexp]
        return r

    def _refresh_regex_labels(self):
        """
        Recalculate labels on model
        :return:
        """
        from django.db import connection
        from noc.models import get_model, is_document

        r = self.get_match_regex_rules()
        for model_id in set(mid for mid, _ in r):
            # Skipping interface for poor performance for $pull operation
            # For 60 second over 12 million
            if model_id != "inv.Interface":
                # Cleanup current labels
                # logger.info("[%s] Cleanup Interface effective labels: %s", self.name, self.name)
                Label.reset_model_labels(model_id, [self.name])
        regxs = defaultdict(list)
        for model_id, field in r:
            if not getattr(self, LABEL_MODELS[model_id], False):
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
                for _, rxs in regxs[model]:
                    params += rxs
                condition = " OR ".join([f"{field} ~ %s" for field, _ in regxs[model]])
                sql = f"""
                UPDATE {model._meta.db_table}
                SET effective_labels=ARRAY (
                SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e)
                )
                WHERE {condition}
                """
                cursor = connection.cursor()
                cursor.execute(sql, params)

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

        def default_iter_effective_labels(instance) -> Iterable[List[str]]:
            yield instance.labels or []

        def on_pre_save(sender, instance=None, document=None, *args, **kwargs):
            instance = instance or document
            # Clean up labels
            labels = Label.merge_labels(default_iter_effective_labels(instance))
            instance.labels = labels
            # Check Match labels
            match_labels = set()
            for ml in getattr(instance, "match_rules", []):
                if is_document(instance):
                    match_labels |= set(ml.labels or [])
                else:
                    match_labels |= set(ml.get("labels", []))
            # Validate instance labels
            can_set_label = getattr(sender, "can_set_label", lambda x: False)
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
            instance.effective_labels = [
                ll
                for ll in Label.merge_labels(labels_iter(instance))
                if can_set_label(ll) or ll[-1] in MATCH_OPS
            ]

        # Install handlers
        if is_document(m_cls):
            from mongoengine import signals as mongo_signals

            mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
        else:
            from django.db.models import signals as django_signals

            django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
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
                                is_protected=False,
                                is_autogenerated=True,
                            )
                    Label.ensure_label(
                        f"noc::{category}::{instance.name}::{matched_scope}{op}",
                        is_protected=False,
                        is_autogenerated=True,
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
    def reset_model_labels(cls, model_id: str, labels: List[str]):
        """
        Unset labels from effective_labels field on models
        :param model_id:
        :param labels:
        :return:
        """
        from django.db import connection

        model = get_model(model_id)
        if is_document(model):
            coll = model._get_collection()
            coll.bulk_write(
                [
                    UpdateMany(
                        {"effective_labels": {"$in": labels}},
                        {"$pull": {"effective_labels": {"$in": labels}}},
                    )
                ]
            )
        else:
            sql = f"""
            UPDATE {model._meta.db_table}
             SET effective_labels=array(
             SELECT unnest(effective_labels) EXCEPT SELECT unnest(%s::varchar[])
             ) WHERE effective_labels && %s::varchar[]
             """
            cursor = connection.cursor()
            cursor.execute(sql, [labels, labels])

    @staticmethod
    def get_instance_profile(
        profile_model,
        instance,
        *args,
        **kwargs,
    ) -> Optional[str]:
        """
        Return Profile ID for instance if it support Labels Classification
        :param instance:
        :param profile_model:
        :param args:
        :param kwargs:
        :return:
        """
        effective_labels = Label.merge_labels(instance.iter_effective_labels(instance))
        if is_document(instance):
            coll = profile_model._get_collection()
            pipeline = [
                {
                    "$match": {
                        "match_rules": {
                            "$elemMatch": {
                                "dynamic_order": {"$ne": 0},
                                "labels": {"$in": effective_labels},
                            }
                        }
                    }
                },
                {"$unwind": "$match_rules"},
                {
                    "$project": {
                        "dynamic_order": "$match_rules.dynamic_order",
                        "labels": "$match_rules.labels",
                        "diff": {"$setDifference": ["$match_rules.labels", effective_labels]},
                        "handlers": 1,
                    }
                },
                {"$match": {"diff": []}},
                {"$sort": {"dynamic_order": 1}},
            ]
            match_profiles = coll.aggregate(pipeline)
        else:
            with connection.cursor() as cursor:
                query = f"""
                                    SELECT pt.id, t.labels, t.dynamic_order, t.handler, match_rules
                                    FROM {profile_model._meta.db_table} as pt
                                    CROSS JOIN LATERAL jsonb_to_recordset(pt.match_rules::jsonb)
                                    AS t("dynamic_order" int, "labels" jsonb, "handler" text)
                                    WHERE t.labels ?| %s::varchar[] order by dynamic_order
                                """
                cursor.execute(query, [effective_labels])
                match_profiles = [
                    {
                        "_id": r[0],
                        "labels": orjson.loads(r[1]),
                        "dynamic_order": r[2],
                        "handler": r[3],
                    }
                    for r in cursor.fetchall()
                ]
        sef = set(effective_labels)
        for profile in match_profiles:
            if "handler" in profile and profile["handler"]:
                handler = Handler.get_by_id(profile["handler"])
                if handler(effective_labels):
                    return profile["_id"]
            if not set(profile["labels"]) - sef:
                return profile["_id"]

    @classmethod
    def dynamic_classification(cls, profile_model_id: str, profile_field: Optional[str] = None):
        def on_post_save(
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
            profile_id = cls.get_instance_profile(profile_model, instance)
            if profile_id and instance.profile.id != profile_id:
                profile = profile_model.get_by_id(profile_id)
                setattr(instance, profile_field, profile)

        def inner(m_cls):
            # Install handlers
            if is_document(m_cls):
                from mongoengine import signals as mongo_signals

                mongo_signals.pre_save.connect(on_post_save, sender=m_cls, weak=False)
            else:
                from django.db.models import signals as django_signals

                django_signals.pre_save.connect(on_post_save, sender=m_cls, weak=False)

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
        operator.attrgetter("_rx_cache"), key=operator.attrgetter("regexp"), lock=lambda _: re_lock
    )
    def _get_re(cls, rxi: "RegexItem") -> Optional[re.Pattern]:
        try:
            rx = re.compile(rxi.regexp)
        except re.error:
            return None
        if rxi.flag_multiline:
            rx.flags ^= re.MULTILINE
        if rxi.flag_dotall:
            rx.flags ^= re.DOTALL
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
    @cachetools.cachedmethod(operator.attrgetter("_rx_labels_cache"), lock=lambda _: rx_labels_lock)
    def get_regex_labels(cls, scope: str) -> Tuple[re.Pattern, str]:
        """
        :param: scope - check `enable_<scope>` for filter enable regex
        """
        rxs = []
        for ll in Label.objects.filter(
            __raw__={"is_regex": True, "match_regex": {"$elemMatch": {"scope": scope}}}
        ):
            for rx in ll.match_regex:
                if rx.scope == scope:
                    rx = cls._get_re(rx)
                    if not rx:
                        continue
                    rxs += [(rx, ll.name)]
        return tuple(rxs)
