# ----------------------------------------------------------------------
# CPE
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import datetime
import logging
from threading import Lock
from typing import Optional, Iterable, List, Any, Dict, Union

# Third-party modules
import bson
import cachetools
from pymongo import UpdateOne, ReadPreference
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    BooleanField,
    DateTimeField,
    DictField,
    EmbeddedDocumentListField,
)
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.models.cfgmetrics import MetricCollectorConfig, MetricItem
from noc.core.validators import is_ipv4
from noc.core.model.decorator import on_delete_check
from noc.core.topology.types import ShapeOverlay, TopologyNode
from noc.core.stencil import Stencil
from noc.main.models.label import Label
from noc.main.models.textindex import full_text_search
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.wf.models.state import State
from noc.inv.models.cpeprofile import CPEProfile
from noc.inv.models.capsitem import CapsItem
from noc.inv.models.capability import Capability
from noc.pm.models.metricrule import MetricRule
from noc.config import config

id_lock = Lock()
CPE_TYPES = IGetCPE.returns.element.attrs["type"].choices
logger = logging.getLogger(__name__)


def check_address(value):
    if not is_ipv4(value):
        raise ValidationError("Bad IPv4 Address: %s" % value)


class ControllerItem(EmbeddedDocument):
    managed_object: ManagedObject = ForeignKeyField(ManagedObject)
    local_id: str = StringField()
    interface = StringField()
    is_active: bool = BooleanField(default=True)

    def __str__(self):
        return f"{self.managed_object.name}: {self.local_id}"

    def get_interface(self):
        if not self.interface:
            return None
        return self.managed_object.get_interface(self.interface)


@full_text_search
@Label.model
@change
@bi_sync
@workflow
@on_delete_check(clean=[("sa.ManagedObject", "cpe_id")])
class CPE(Document):
    meta = {
        "collection": "cpes",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "controllers",
            "global_id",
            "labels",
            "effective_labels",
            {
                "fields": ["controllers.managed_object"],
                "partialFilterExpression": {"controllers.active": True},
            },
            # {"fields": ("controllers.controller", "controllers.local_id"), "unique": True},
        ],
    }

    # (<managed object>, <local_id>) Must be unique
    controllers: List[ControllerItem] = EmbeddedDocumentListField(ControllerItem)
    global_id = StringField(unique=True)
    # Probe profile
    profile: CPEProfile = PlainReferenceField(CPEProfile, default=CPEProfile.get_default_profile)
    # Optional description
    description = StringField()
    # State
    state: State = PlainReferenceField(State)
    # Oper Status
    oper_status = BooleanField(required=False)
    oper_status_change = DateTimeField(required=False)
    # Timestamp of last seen
    last_seen = DateTimeField()
    # Timestamp expired
    expired = DateTimeField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Probe type
    type = StringField(choices=[(x, x) for x in CPE_TYPES], default="other")
    # IPv4 CPE address, used for ManagedObject sync
    address = StringField(validation=check_address)
    #
    label = StringField(required=False)
    # Capabilities
    caps: List[CapsItem] = EmbeddedDocumentListField(CapsItem)
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    extra_labels = DictField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.label or str(self.controller)

    def __repr__(self):
        return str(self.controller)

    @property
    def controller(self) -> Optional[ControllerItem]:
        for c in self.controllers:
            if c.is_active:
                return c
        return

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["CPE"]:
        return CPE.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["CPE"]:
        return CPE.objects.filter(bi_id=bi_id).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmetricsources:
            yield "cfgmetricsources", f"inv.CPE::{self.bi_id}"

    def clean(self):
        if self.extra_labels:
            self.labels += [
                ll for ll in Label.merge_labels(self.extra_labels.values()) if CPE.can_set_label(ll)
            ]

    @classmethod
    def iter_effective_labels(cls, instance: "CPE") -> List[str]:
        yield list(instance.labels or [])
        if instance.profile.labels:
            yield list(instance.profile.labels)
        if not instance.controller:
            return
        yield [
            ll
            for ll in instance.controller.managed_object.get_effective_labels()
            if ll != "noc::is_linked::="
        ]

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_managedobject")

    @classmethod
    def _reset_caches(cls, cpe_id: int):
        try:
            del cls._id_cache[str(cpe_id),]
        except KeyError:
            pass

    def seen(
        self,
        controller: Optional[ManagedObject] = None,
        local_id: Optional[str] = None,
        interface: Optional[str] = None,
        status: bool = True,
    ):
        """
        Seen sensor
        """
        if not controller or not local_id:
            self.fire_event("seen")
            self.touch()  # Worflow expired
            return
        changes = {}
        seen = False
        for c in self.controllers:
            if c.managed_object != controller:
                continue
            seen = True
            if c.local_id != local_id:
                c.local_id = local_id
                changes["controllers.$.local_id"] = local_id
            if c.interface != interface:
                c.interface = interface
                changes["controllers.$.interface"] = interface
            if c.is_active != status:
                c.is_active = status
                changes["controllers.$.is_active"] = status
        if not seen:
            # New Controller
            self.controllers += [
                ControllerItem(
                    managed_object=controller,
                    local_id=local_id,
                    interface=interface,
                    is_active=status,
                )
            ]
            self._get_collection().update_one(
                {"_id": self.id},
                {
                    "$push": {
                        "managed_object": controller.id,
                        "local_id": local_id,
                        "interface": interface,
                        "is_active": status,
                    }
                },
            )
        elif changes:
            self._get_collection().update_one(
                {"_id": self.id, "controllers": {"$elemMatch": {"managed_object": controller.id}}},
                {"$set": changes},
            )
        self.fire_event("seen")
        self.touch()  # Worflow expired

    def unseen(self, controller: Optional[str] = None):
        """
        Unseen sensor
        """
        logger.info("[%s] CPE is missed on '%s'", self.global_id, controller)
        if controller:
            self.controllers = [c for c in self.controllers if c.managed_object != controller]
            self._get_collection().update_one(
                {"_id": self.id}, {"$pull": {"controllers": {"managed_object": controller.id}}}
            )
        elif not controller:
            # For empty source, clean sources
            self.controllers = []
            self._get_collection().update_one({"_id": self.id}, {"$set": {"controllers": []}})
        if not self.controllers:
            # source - None, set sensor to missed
            self.fire_event("missed")
            self.touch()

    @classmethod
    def get_component(
        cls, managed_object, global_id: str = None, local_id: str = None, **kwargs
    ) -> Optional["CPE"]:
        if not global_id or not local_id:
            return
        if global_id:
            return CPE.objects.filter(global_id=global_id).first()
        if local_id:
            return CPE.objects.filter(
                controllers__match={"managed_object": managed_object, "local_id": local_id}
            ).first()

    @classmethod
    def iter_collected_metrics(
        cls, mo: "ManagedObject", run: int = 0, d_interval: Optional[int] = None
    ) -> Iterable[MetricCollectorConfig]:
        """
        Return metrics setting for collected
        :param mo: MangedObject that run job
        :param run: Number of job run
        :return:
        """
        caps = mo.get_caps()
        cpe_count = caps.get("DB | CPEs")
        if not cpe_count:
            return
        d_interval = d_interval or mo.get_metric_discovery_interval()
        # logger.info("Sharding mode activated. Buckets: %d", buckets)
        for cpe in CPE.objects.filter(
            controllers__match={"managed_object": mo.id, "is_active": True}
        ).read_preference(ReadPreference.SECONDARY_PREFERRED):
            if not cpe.state.is_productive:
                continue
            buckets = cpe.profile.metrics_interval_buckets
            if not buckets:
                # Auto calculate buckets count
                m_interval = cpe.profile.get_metric_discovery_interval()
                buckets = max(1, round(m_interval / d_interval))
            if buckets != 1 and run and cpe.bi_id % buckets != run % buckets:
                # Sharder mode, skip inactive shard
                continue
            metrics = []
            for metric in cpe.profile.metrics:
                mi = MetricItem(
                    name=metric.metric_type.name,
                    field_name=metric.metric_type.field_name,
                    scope_name=metric.metric_type.scope.table_name,
                    is_stored=metric.is_stored,
                    is_compose=metric.metric_type.is_compose,
                    interval=metric.interval or cpe.profile.metrics_default_interval or d_interval,
                )
                if mi.is_run(d_interval, cpe.bi_id, buckets, run):
                    metrics.append(mi)
            if not metrics:
                logger.debug("CPE metrics are not configured. Skipping")
                continue
            labels, hints = [f"noc::chassis::{cpe.global_id}"], [
                f"cpe_type::{cpe.type}",
                f"local_id::{cpe.controller.local_id}",
            ]
            if cpe.controller.interface:
                iface = cpe.controller.get_cpe_interface()
                if iface and iface.ifindex:
                    hints += [f"ifindex::{iface.ifindex}"]
            yield MetricCollectorConfig(
                collector="cpe",
                metrics=tuple(metrics),
                labels=tuple(labels),
                hints=hints,
                cpe=cpe.bi_id,
                # service=self.service,
            )

    @classmethod
    def get_metric_config(cls, cpe: "CPE"):
        """
        Return MetricConfig for Metrics service
        :param cpe:
        :return:
        """
        if not cpe.state.is_productive:
            return {}
        labels = []
        for ll in cpe.effective_labels:
            l_c = Label.get_by_name(ll)
            labels.append({"label": ll, "expose_metric": l_c.expose_metric if l_c else False})
        return {
            "type": "cpe",
            "bi_id": cpe.bi_id,
            "fm_pool": cpe.controller.managed_object.get_effective_fm_pool().name,
            "labels": labels,
            "metrics": [
                {"name": mc.metric_type.field_name, "is_stored": mc.is_stored}
                for mc in cpe.profile.metrics
            ],
            "rules": [ma for ma in MetricRule.iter_rules_actions(cpe.effective_labels)],
            "sharding_key": cpe.controller.managed_object.bi_id if cpe.controller else None,
            "items": [],
        }

    @property
    def has_configured_metrics(self) -> bool:
        """
        Check configured collected metrics
        :return:
        """
        config = self.get_metric_config(self)
        return config.get("metrics") or config.get("items")

    def get_cpe_interface(self):
        return self.controller.get_interface()

    def update_caps(
        self, caps: Dict[str, Any], source: str, scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update existing capabilities with a new ones.
        :param caps: dict of caps name -> caps value
        :param source: Source name
        :param scope: Scope name
        """

        o_label = f"{scope or ''}|{self}|{source}"
        # Update existing capabilities
        new_caps = []
        seen = set()
        changed = False
        for ci in self.caps:
            c = ci.capability
            cs = ci.source
            css = ci.scope or ""
            cv = ci.value
            if not c:
                logger.info("[%s] Removing unknown capability id %s", o_label, ci["capability"])
                continue
            cv = c.clean_value(cv)
            cn = c.name
            seen.add(cn)
            if scope and scope != css:
                logger.info(
                    "[%s] Not changing capability %s: from other scope '%s'",
                    o_label,
                    cn,
                    css,
                )
            elif cs == source:
                if cn in caps:
                    if caps[cn] != cv:
                        logger.info(
                            "[%s] Changing capability %s: %s -> %s", o_label, cn, cv, caps[cn]
                        )
                        ci["value"] = caps[cn]
                        changed = True
                else:
                    logger.info("[%s] Removing capability %s", o_label, cn)
                    changed = True
                    continue
            elif cn in caps:
                logger.info(
                    "[%s] Not changing capability %s: Already set with source '%s'",
                    o_label,
                    cn,
                    cs,
                )
            new_caps += [ci]
        # Add new capabilities
        for cn in set(caps) - seen:
            c = Capability.get_by_name(cn)
            if not c:
                logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
                continue
            logger.info("[%s] Adding capability %s = %s", o_label, cn, caps[cn])
            new_caps += [CapsItem(capability=c, value=caps[cn], source=source, scope=scope or "")]
            changed = True

        if changed:
            logger.info("[%s] Saving changes", o_label)
            self.caps = new_caps
            self.update(caps=self.caps)
            self._reset_caches(self.id)
        caps = {}
        for ci in new_caps:
            cn = ci.capability
            if cn:
                caps[cn.name] = ci.value
        return caps

    def get_caps(self) -> Dict[str, Any]:
        return CapsItem.get_caps(self.caps)

    def set_oper_status(
        self,
        status: bool,
        change_ts: Optional[datetime.datetime] = None,
        bulk: Optional[List[Any]] = None,
    ):
        """
        Set oper CPE status
        :param status:
        :param bulk: List for append bulk op
        :param change_ts: Status change Timestamp
        :return:
        """
        now = datetime.datetime.now()
        change_ts = change_ts or now
        if self.oper_status != status and (
            not self.oper_status_change or self.oper_status_change < now
        ):
            self.oper_status = status
            self.oper_status_change = change_ts
            if bulk is not None:
                self.update(oper_status=status, oper_status_change=change_ts)
            else:
                bulk += [
                    UpdateOne(
                        {"_id": self.id},
                        {"$set": {"oper_status": status, "oper_status_change": change_ts}},
                    )
                ]

    def get_index(self):
        """
        Get FTS index
        """
        card = f"CPE object {self.global_id} ({self.address})"
        content: List[str] = [self.global_id, self.address]
        if self.description:
            content += [self.description]
        r = {
            "title": f"{self.global_id} {self.controller}",
            "content": "\n".join(content),
            "card": card,
            "tags": self.labels,
        }
        return r

    @classmethod
    def get_search_result_url(cls, obj_id):
        return f"/api/card/view/cpe/{obj_id}/"

    @classmethod
    def get_metric_discovery_interval(cls, mo: "ManagedObject") -> int:
        coll = cls._get_collection()
        r = coll.aggregate(
            [
                {
                    "$match": {
                        "controllers": {"$elemMatch": {"managed_object": mo.id, "is_active": True}}
                    }
                },
                {
                    "$lookup": {
                        "from": "cpeprofiles",
                        "localField": "profile",
                        "foreignField": "_id",
                        "as": "profiles",
                    }
                },
                {"$unwind": "$profiles"},
                {"$match": {"profiles.metrics": {"$ne": []}}},
                {
                    "$project": {
                        "interval": {
                            "$min": [
                                {"$min": "$profiles.metrics.interval"},
                                "$profiles.metrics_default_interval",
                            ]
                        }
                    }
                },
                {"$group": {"_id": "", "interval": {"$min": "$interval"}}},
            ]
        )
        r = next(r, {})
        return r.get("interval", 0)

    def get_stencil(self) -> Optional[Stencil]:
        if self.profile.shape:
            # Use profile's shape
            return self.profile.shape
        return

    def get_shape_overlays(self) -> List[ShapeOverlay]:
        return []

    def get_topology_node(self) -> TopologyNode:
        return TopologyNode(
            id=str(self.id),
            type="cpe",
            resource_id=str(self.id),
            title=str(self),
            title_metric_template=self.profile.shape_title_template or "",
            stencil=self.get_stencil(),
            overlays=self.get_shape_overlays(),
            level=10,
            attrs={
                "address": self.address,
                "mo": self.controller.managed_object,
                "caps": self.get_caps(),
            },
        )
