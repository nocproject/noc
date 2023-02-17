# ----------------------------------------------------------------------
# CPE
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import datetime
import logging
from threading import Lock
from typing import Optional, Iterable, List, Any, Dict

# Third-party modules
import cachetools
from pymongo import UpdateOne
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    BooleanField,
    DateTimeField,
    DictField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.models.cfgmetrics import MetricCollectorConfig, MetricItem
from noc.core.validators import is_ipv4
from noc.core.model.decorator import on_delete_check
from noc.main.models.label import Label
from noc.main.models.textindex import full_text_search
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.wf.models.state import State
from noc.inv.models.cpeprofile import CPEProfile
from noc.inv.models.capsitem import CapsItem
from noc.inv.models.capability import Capability
from noc.config import config

id_lock = Lock()
CPE_TYPES = IGetCPE.returns.element.attrs["type"].choices
logger = logging.getLogger(__name__)


@full_text_search
@Label.model
@change
@bi_sync
@workflow
@on_delete_check(clean=[("sa.ManagedObject", "managed_object")])
class CPE(Document):
    meta = {
        "collection": "cpes",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "controller",
            "global_id",
            "labels",
            "effective_labels",
            {"fields": ["controller", "local_id"], "unique": True},
        ],
    }

    controller: ManagedObject = ForeignKeyField(ManagedObject)
    interface = StringField()
    # (<managed object>, <local_id>) Must be unique
    local_id = StringField()
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
    type = StringField(choices=[(x, x) for x in CPE_TYPES])
    # IPv4 CPE address, used for ManagedObject sync
    address = StringField(validation=is_ipv4)
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
        return f"{self.controller}: {self.local_id}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, cpe_id) -> Optional["CPE"]:
        return CPE.objects.filter(id=cpe_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, cpe_id) -> Optional["CPE"]:
        return CPE.objects.filter(bi_id=cpe_id).first()

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
        yield [ll for ll in instance.controller.get_effective_labels() if ll != "noc::is_linked::="]

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_managedobject")

    @classmethod
    def _reset_caches(cls, cpe_id: int):
        try:
            del cls._id_cache[str(cpe_id),]
        except KeyError:
            pass

    @classmethod
    def get_component(
        cls, managed_object, global_id: str = None, local_id: str = None, **kwargs
    ) -> Optional["CPE"]:
        if not global_id or not local_id:
            return
        if global_id:
            return CPE.objects.filter(global_id=global_id).first()
        if local_id:
            return CPE.objects.filter(controller=managed_object, local_id=local_id).first()

    def iter_collected_metrics(self) -> Iterable[MetricCollectorConfig]:
        """
        Return metrics setting for collected
        :return:
        """
        if not self.state.is_productive or not self.controller:
            return
        metrics = []
        for metric in self.profile.metrics:
            interval = metric.interval or self.profile.metrics_default_interval
            if not interval:
                continue
            metrics += [
                MetricItem(
                    name=metric.metric_type.name,
                    field_name=metric.metric_type.field_name,
                    scope_name=metric.metric_type.scope.table_name,
                    is_stored=metric.is_stored,
                    is_compose=metric.metric_type.is_compose,
                    interval=interval,
                )
            ]
        if not metrics:
            # self.logger.info("SLA metrics are not configured. Skipping")
            return
        labels, hints = [f"noc::chassis::{self.global_id}"], [
            f"cpe_type::{self.type}",
            f"local_id::{self.local_id}",
        ]
        if self.interface:
            labels += [f"noc::interface::{self.interface}"]
            iface = self.get_cpe_interface()
            if iface and iface.ifindex:
                hints += [f"ifindex::{iface.ifindex}"]
        yield MetricCollectorConfig(
            collector="cpe",
            metrics=tuple(metrics),
            labels=tuple(labels),
            hints=hints,
            cpe=self.bi_id,
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
            "fm_pool": cpe.controller.get_effective_fm_pool().name,
            "labels": labels,
            "metrics": [
                {"name": mc.metric_type.field_name, "is_stored": mc.is_stored}
                for mc in cpe.profile.metrics
            ],
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
        if not self.interface:
            return None
        return self.controller.get_interface(self.interface)

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
