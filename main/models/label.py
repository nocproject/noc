# ----------------------------------------------------------------------
# Label model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Set, Iterable
from threading import Lock
import operator
from itertools import accumulate

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField, ReferenceField
import cachetools

# NOC modules
from noc.core.model.decorator import on_save, on_delete, is_document
from noc.main.models.remotesystem import RemoteSystem


id_lock = Lock()


@on_save
@on_delete
class Label(Document):
    meta = {
        "collection": "labels",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(unique=True)
    description = StringField()
    bg_color1 = IntField(default=0x000000)
    fg_color1 = IntField(default=0xFFFFFF)
    bg_color2 = IntField(default=0x000000)
    fg_color2 = IntField(default=0xFFFFFF)
    # Restrict UI operations
    is_protected = BooleanField(default=False)
    # Label scope
    enable_agent = BooleanField()
    enable_service = BooleanField()
    enable_serviceprofile = BooleanField()
    enable_managedobject = BooleanField()
    enable_managedobjectprofile = BooleanField()
    enable_administrativedomain = BooleanField()
    enable_authprofile = BooleanField()
    enable_commandsnippet = BooleanField()
    #
    enable_allocationgroup = BooleanField()
    enable_networksegment = BooleanField()
    enable_object = BooleanField()
    enable_objectmodel = BooleanField()
    enable_platform = BooleanField()
    enable_resourcegroup = BooleanField()
    enable_sensorprofile = BooleanField()
    #
    enable_subscriber = BooleanField()
    enable_subscriberprofile = BooleanField()
    enable_supplier = BooleanField()
    enable_supplierprofile = BooleanField()
    #
    enable_dnszone = BooleanField()
    enable_dnszonerecord = BooleanField()
    #
    enable_division = BooleanField()
    #
    enable_kbentry = BooleanField()
    # IP
    enable_ipaddress = BooleanField()
    enable_addressprofile = BooleanField()
    enable_ipaddressrange = BooleanField()
    enable_ipprefix = BooleanField()
    enable_prefixprofile = BooleanField()
    enable_vrf = BooleanField()
    enable_vrfgroup = BooleanField()
    # Peer
    enable_asn = BooleanField()
    enable_assetpeer = BooleanField()
    enable_peer = BooleanField()
    # VC
    enable_vc = BooleanField()
    enable_vlan = BooleanField()
    enable_vlanprofile = BooleanField()
    enable_vpn = BooleanField()
    enable_vpnprofile = BooleanField()
    # SLA
    enable_slaprobe = BooleanField()
    enable_slaprofile = BooleanField()
    # FM
    enable_alarm = BooleanField()
    # Exposition scope
    expose_metric = BooleanField()
    expose_datastream = BooleanField()
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _setting_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    def clean(self):
        # Wildcard labels are protected
        if self.is_wildcard:
            self.is_protected = True

    def on_save(self):
        if self.is_scoped and not self.is_wildcard:
            self._ensure_wildcards()

    def on_delete(self):
        if self.is_wildcard and any(Label.objects.filter(name__startswith=self.name[:-1])):
            raise ValueError("Cannot delete wildcard label with matched labels")
        if self.is_builtin:
            raise ValueError("Cannot delete builtin label with matched labels")

    @staticmethod
    def get_wildcards(label: str) -> List[str]:
        return [label] + [
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
                    {"$match": {"name": {"$in": wildcards}}},
                    {"$group": {"_id": None, setting: {"$max": f"${setting}"}}},
                ]
            ),
            {},
        )
        return bool(r.get(setting))

    @property
    def effective_settings(self):
        """
        Returns dict with effective settings
        """
        es = {ff: False for ff in self._fields if ff.startswith("enable")}
        wildcards = self.get_wildcards(self.name)
        coll = self._get_collection()
        group = {setting: {"$max": f"${setting}"} for setting in es}
        group["_id"] = None
        r = next(
            coll.aggregate(
                [
                    {"$match": {"name": {"$in": wildcards}}},
                    {"$group": group},
                    {"$project": {"_id": -1}},
                ]
            ),
            {},
        )
        es.update(r)
        return es

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
                elif "::" in label:
                    scope = label.rsplit("::", 1)[0]
                    if scope in seen_scopes:
                        continue
                    seen_scopes.add(scope)
                r.append(label)
                seen.add(label)
        return r

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
        Returns True if the label is protected
        :return:
        """
        return self.name.endswith("::*")

    @property
    def is_builtin(self) -> bool:
        """
        Returns True if the label is protected
        :return:
        """
        return self.name.startswith("noc::")

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
        if Label.objects.filter(name=name).first():  # Do not use get_by_name. Cached None !
            return  # Exists
        Label(
            name=name,
            description=description or "Auto-created",
            is_protected=is_protected,
            bg_color1=bg_color1,
            fg_color1=fg_color1,
            bg_color2=bg_color2,
            fg_color2=fg_color2,
            expose_metric=expose_metric,
            expose_datastream=expose_datastream,
        ).save()

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
                is_protected=True,
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
            # Validate instance labels
            can_set_label = getattr(sender, "can_set_label", lambda x: False)
            for label in set(instance.labels):
                if not can_set_label(label):
                    # Check can_set_label method
                    raise ValueError(f"Invalid label: {label}")
            # Build and clean up effective labels. Filter can_set_labels
            labels_iter = getattr(sender, "iter_effective_labels", default_iter_effective_labels)
            instance.effective_labels = [
                ll for ll in Label.merge_labels(labels_iter(instance)) if can_set_label(ll)
            ]

        # Install handlers
        if is_document(m_cls):
            from mongoengine import signals as mongo_signals

            mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
        else:
            from django.db.models import signals as django_signals

            django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
        return m_cls
