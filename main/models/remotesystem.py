# ----------------------------------------------------------------------
# RemoteSystem model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import datetime
from threading import Lock
from typing import Optional, Union, List, Dict, Tuple, Any

# Third-party modules
import bson
import orjson
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    EmbeddedDocumentListField,
    ReferenceField,
    BooleanField,
    DateTimeField,
    LongField,
    IntField,
)

# NOC modules
from noc.core.model.decorator import on_delete_check, on_save, on_delete
from noc.core.handler import get_handler
from noc.core.bi.decorator import bi_sync
from noc.core.debug import error_report
from noc.core.mx import send_message, MessageType, MessageMeta, get_subscription_id
from noc.core.scheduler.scheduler import Scheduler
from noc.core.etl.remotesystem.base import BaseRemoteSystem, StepResult
from noc.core.etl.portmapper.loader import loader as portmapper_loader
from noc.core.etl.portmapper.base import BasePortMapper
from noc.core.change.decorator import change
from noc.aaa.models.apikey import APIKey
from noc.config import config

id_lock = Lock()
REFERENCE_CODE = "rs"


class EnvItem(EmbeddedDocument):
    """
    Environment item
    """

    key = StringField()
    value = StringField()

    def __str__(self):
        return self.key


@bi_sync
@change
@on_delete
@on_save
@on_delete_check(
    check=[
        ("crm.Subscriber", "remote_system"),
        ("crm.SubscriberProfile", "remote_system"),
        ("crm.Supplier", "remote_system"),
        ("crm.SupplierProfile", "remote_system"),
        ("inv.ExtNRILink", "remote_system"),
        ("fm.ActiveAlarm", "remote_system"),
        ("fm.ArchivedAlarm", "remote_system"),
        ("fm.TTSystem", "remote_system"),
        ("gis.Address", "remote_system"),
        ("gis.Building", "remote_system"),
        ("gis.Division", "remote_system"),
        ("gis.Street", "remote_system"),
        ("inv.AllocationGroup", "remote_system"),
        ("inv.InterfaceProfile", "remote_system"),
        ("inv.NetworkSegment", "remote_system"),
        ("inv.NetworkSegmentProfile", "remote_system"),
        ("inv.ResourceGroup", "remote_system"),
        ("inv.Sensor", "remote_system"),
        ("inv.Object", "remote_system"),
        ("ip.VRF", "remote_system"),
        ("ip.AddressProfile", "remote_system"),
        ("ip.Address", "remote_system"),
        ("ip.PrefixProfile", "remote_system"),
        ("ip.Prefix", "remote_system"),
        ("main.Label", "remote_system"),
        ("sa.ManagedObject", "remote_system"),
        ("sa.AdministrativeDomain", "remote_system"),
        ("sa.ManagedObjectProfile", "remote_system"),
        ("sa.AuthProfile", "remote_system"),
        ("sa.ServiceProfile", "remote_system"),
        ("sa.ReactionRule", "conditions__remote_system"),
        ("inv.Channel", "remote_system"),
        ("inv.ResourceGroup", "remote_system"),
        ("sa.Service", "remote_system"),
        ("pm.Agent", "remote_system"),
        ("vc.VLAN", "remote_system"),
        ("vc.VLANProfile", "remote_system"),
        ("vc.VPN", "remote_system"),
        ("vc.VPNProfile", "remote_system"),
        ("vc.L2Domain", "remote_system"),
        ("vc.L2DomainProfile", "remote_system"),
        ("wf.State", "remote_system"),
        ("wf.Transition", "remote_system"),
        ("wf.Workflow", "remote_system"),
        ("project.Project", "remote_system"),
        ("maintenance.Maintenance", "remote_system"),
    ],
    delete=[("main.NotificationGroupSubscription", "remote_system")],
)
class RemoteSystem(Document):
    meta = {
        "collection": "noc.remotesystem",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["remote_collectors_policy"],
    }

    name = StringField(unique=True)
    description = StringField()
    handler = StringField()
    # Environment variables
    environment = EmbeddedDocumentListField(EnvItem)
    # Enable extractors/loaders
    enable_address = BooleanField()
    enable_admdiv = BooleanField()
    enable_administrativedomain = BooleanField()
    enable_authprofile = BooleanField()
    enable_building = BooleanField()
    enable_container = BooleanField()
    enable_link = BooleanField()
    enable_managedobject = BooleanField()
    enable_managedobjectprofile = BooleanField()
    enable_networksegment = BooleanField()
    enable_networksegmentprofile = BooleanField()
    enable_object = BooleanField()
    enable_sensor = BooleanField()
    enable_service = BooleanField()
    enable_serviceprofile = BooleanField()
    enable_street = BooleanField()
    enable_subscriber = BooleanField()
    enable_subscriberprofile = BooleanField()
    enable_resourcegroup = BooleanField()
    enable_ttsystem = BooleanField()
    enable_project = BooleanField()
    enable_l2domain = BooleanField()
    enable_ipvrf = BooleanField()
    enable_ipprefix = BooleanField()
    enable_ipprefixprofile = BooleanField()
    enable_ipaddress = BooleanField()
    enable_ipaddressprofile = BooleanField()
    enable_label = BooleanField()
    enable_discoveredobject = BooleanField()
    enable_pmagent = BooleanField()
    enable_fmevent = BooleanField()
    enable_metrics = BooleanField()
    enable_maintenance = BooleanField()
    api_key: Optional[APIKey] = ReferenceField(APIKey)
    remote_collectors_policy: str = StringField(
        choices=[
            ("D", "Disable"),
            ("E", "Enable"),
            ("S", "Strict"),
        ],
        default="D",
    )
    remote_collectors_batch_signal = StringField(
        choices=[("A", "Any"), ("D", "Delay Only"), ("B", "Batch Only")],
        default="D",
    )
    metrics_min_batch_size: int = IntField(min_value=1000, default=5000)
    metrics_batch_delay: int = IntField(min_value=5, default=10)
    portmapper_name = StringField()
    managed_object_loader_policy = StringField(
        choices=[("D", "As Discovered"), ("M", "As Managed Object")],
        default="M",
    )
    # Run Sync
    sync_policy = StringField(
        choices=[
            ("M", "Manual"),
            ("P", "Period"),
            ("C", "Cron"),
        ],
        default="M",
    )
    run_sync_at = DateTimeField()
    sync_interval = IntField()
    sync_notification = StringField(
        choices=[("D", "Disable"), ("F", "Failed Only"), ("A", "All")], default="F"
    )
    # raise_alarm_if_failed = StringField(choices=[("D", "Disable"), ("A", "Alarm")], default="A")
    sync_lock = BooleanField(default=False)
    event_sync_interval = IntField(default=0)
    event_sync_mode = StringField(
        choices=[("I", "incremental"), ("S", "Snapshot"), ("P", "Push")],
        default="I",
    )
    event_sync_lock = BooleanField(default=False)
    # TTL Settings
    # Usage statistics
    last_extract = DateTimeField()
    last_successful_extract = DateTimeField()
    extract_error = StringField()
    last_load = DateTimeField()
    last_successful_load = DateTimeField()
    last_extract_event = DateTimeField()
    last_successful_extract_event = DateTimeField()
    last_extract_metrics = DateTimeField()
    last_successful_extract_metrics = DateTimeField()
    load_error = StringField()
    object_url_template = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _api_key_cache = cachetools.TTLCache(maxsize=10, ttl=60)
    _active_collector = cachetools.TTLCache(maxsize=10, ttl=120)

    SCHEDULER = "scheduler"
    JCLS = "noc.services.scheduler.jobs.remote_system.ETLSyncJob"
    JCLS_EVENT = "noc.services.scheduler.jobs.remote_system.ETLEventSyncJob"
    JCLS_METRIC = "noc.services.scheduler.jobs.remote_system.ETLMetricSyncJob"
    # Sync Event

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["RemoteSystem"]:
        return RemoteSystem.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["RemoteSystem"]:
        return RemoteSystem.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["RemoteSystem"]:
        return RemoteSystem.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_api_key_cache"), lock=lambda _: id_lock)
    def get_by_api_key(cls, api_key: str) -> Optional["RemoteSystem"]:
        api_key = APIKey.get_by_api_key(api_key)
        if api_key:
            return RemoteSystem.objects.filter(api_key=api_key).first()
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_active_collector"), lock=lambda _: id_lock)
    def has_active_remote_collector(cls) -> bool:
        """Check active remote collector"""
        return bool(RemoteSystem.objects.filter(remote_collectors_policy="E").first())

    @property
    def config(self) -> Dict[str, str]:
        if not hasattr(self, "_config"):
            self._config = {e.key: e.value for e in self.environment}
        return self._config

    @property
    def managed_object_as_discovered(self) -> bool:
        return self.managed_object_loader_policy == "D"

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        changed_fields = set(changed_fields or [])
        if config.datastream.enable_cfgtarget and changed_fields.intersection(
            {
                "name",
                "api_key",
                "remote_collectors_policy",
                "enable_fmevent",
            }
        ):
            if self.remote_collectors_policy == "S":
                for mo_id in ManagedObject.objects.filter(remote_system=self).values_list(
                    "id", flat=True
                ):
                    yield "cfgtarget", mo_id
            else:
                for mo_id in ManagedObject.objects.filter().values_list("id", flat=True):
                    yield "cfgtarget", mo_id
        if config.datastream.enable_cfgmetricstarget:
            yield "cfgmetricstarget", f"main.RemoteSystem::{self.bi_id}"

    def get_portmapper(self) -> "BasePortMapper":
        """Getting portmapper functions"""
        p_name = self.portmapper_name or self.name
        return portmapper_loader[p_name]

    def get_handler(self) -> BaseRemoteSystem:
        """Return BaseRemoteSystem instance"""
        h = get_handler(str(self.handler))
        if not h:
            raise ValueError
        return h(self)

    def get_extractors(self, exclude_fmevent: bool = False) -> List[str]:
        extractors = []
        for k in self._fields:
            if k.startswith("enable_") and getattr(self, k):
                if exclude_fmevent and k == "enable_fmevent":
                    continue
                extractors += [k[7:]]
        return extractors

    def extract(
        self,
        extractors: Optional[List[str]] = None,
        quiet: bool = False,
        incremental: bool = False,
        checkpoint: Optional[str] = None,
        exclude_fmevent: Optional[bool] = False,
    ) -> List[StepResult]:
        extractors = extractors or self.get_extractors(exclude_fmevent=exclude_fmevent)
        error, results = None, []
        try:
            results = self.get_handler().extract(
                extractors, incremental=incremental, checkpoint=checkpoint
            )
        except PermissionError as e:
            error_report(suppress_log=True)
            error = str(e)
        except Exception as e:
            if not quiet:
                raise e
            error_report(suppress_log=quiet)
            error = str(e)
        self.last_extract = datetime.datetime.now().replace(microsecond=0)
        if not error:
            self.last_successful_extract = self.last_extract
        events_result = [r for r in results if r.loader == "fmevent"]
        if events_result:
            self.last_extract_event = self.last_extract
            if not error:
                self.last_successful_extract_event = self.last_extract
        self.extract_error = error
        if events_result and len(events_result) == 1:
            # For event extract, Save event only fields
            RemoteSystem.objects.filter(id=self.id).update(
                last_extract_event=self.last_extract_event,
                extract_error=error,
                last_successful_extract_event=self.last_successful_extract_event,
            )
        else:
            RemoteSystem.objects.filter(id=self.id).update(
                last_extract=self.last_extract,
                last_extract_event=self.last_extract_event,
                extract_error=error,
                last_successful_extract=self.last_successful_extract,
                last_successful_extract_event=self.last_successful_extract_event,
            )
        # self.save()
        return results

    def load(
        self,
        extractors: Optional[List[str]] = None,
        quiet: bool = False,
        exclude_fmevent: bool = False,
    ) -> Optional[List[StepResult]]:
        extractors = extractors or self.get_extractors(exclude_fmevent=exclude_fmevent)
        error, r = None, []
        try:
            r = self.get_handler().load(extractors)
        except Exception as e:
            if not quiet:
                raise e
            error_report(suppress_log=quiet)
            error = str(e)
        self.last_load = datetime.datetime.now().replace(microsecond=0)
        if not error:
            self.last_successful_load = self.last_load
        self.load_error = error
        RemoteSystem.objects.filter(id=self.id).update(
            last_load=self.last_load,
            load_error=error,
            last_successful_load=self.last_successful_load,
        )
        # self.save()
        return r

    def check(
        self, extractors: Optional[List[str]] = None, out=None
    ) -> Optional[Tuple[int, List[StepResult]]]:
        extractors = extractors or self.get_extractors()
        try:
            return self.get_handler().check(extractors, out=out)
        except Exception:
            error_report()

    def register_error(
        self,
        step: str,
        error: str,
        recommended_actions: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        ts = ts or datetime.datetime.now()
        send_message(
            {
                "remote_system": {"name": self.name, "id": str(self.id)},
                "ts": ts.replace(microsecond=0).isoformat(),
                "step": step,
                "error": error,
                "recommended_actions": recommended_actions,
                "retry_at": "",
            },
            message_type=MessageType.ETL_SYNC_FAILED,
            headers=self.get_mx_message_headers(),
        )

    def get_metric_extractor(self):
        """Extract metrics from RemoteSystem"""
        return self.get_handler().get_metric_extractor()

    def get_loader_chain(self):
        return self.get_handler().get_loader_chain()

    @property
    def enable_sync(self) -> bool:
        return self.sync_policy != "M"

    def get_mx_message_headers(self) -> Dict[str, bytes]:
        return {
            key.config.header: key.clean_header_value(value)
            for key, value in self.message_meta.items()
        }

    @property
    def message_meta(self) -> Dict[MessageMeta, Any]:
        """Message Meta for instance"""
        return {
            MessageMeta.WATCH_FOR: get_subscription_id(self),
        }

    def on_save(self):
        self.ensure_job()
        self.ensure_event_job()
        self.ensure_metric_job()

    def on_delete(self):
        scheduler = Scheduler(self.SCHEDULER)
        scheduler.remove_job(jcls=self.JCLS, key=self.id)
        scheduler.remove_job(jcls=self.JCLS_EVENT, key=self.id)

    def ensure_job(self):
        """Create or remove scheduler job"""
        scheduler = Scheduler(self.SCHEDULER)
        if self.enable_sync and self.sync_interval:
            ts = self.run_sync_at or datetime.datetime.now().replace(microsecond=0)
            if ts:
                scheduler.submit(jcls=self.JCLS, key=self.id, ts=ts)
                return
        scheduler.remove_job(jcls=self.JCLS, key=self.id)

    def ensure_event_job(self):
        """Create or remove scheduler job"""
        scheduler = Scheduler(self.SCHEDULER)
        if self.enable_sync and self.event_sync_interval:
            ts = self.run_sync_at or datetime.datetime.now().replace(microsecond=0)
            if ts:
                scheduler.submit(jcls=self.JCLS_EVENT, key=self.id, ts=ts)
                return
        scheduler.remove_job(jcls=self.JCLS_EVENT, key=self.id)

    def ensure_metric_job(self):
        """Create or remove scheduler job"""
        scheduler = Scheduler(self.SCHEDULER)
        if self.enable_metrics and self.remote_collectors_policy == "D":
            ts = self.run_sync_at or datetime.datetime.now().replace(microsecond=0)
            if ts:
                scheduler.submit(jcls=self.JCLS_METRIC, key=self.id, ts=ts)
                return
        scheduler.remove_job(jcls=self.JCLS_METRIC, key=self.id)

    @classmethod
    def get_collector_config(cls, remote_system: "RemoteSystem") -> Dict[str, Any]:
        """Collector config"""
        if remote_system.remote_collectors_policy != "D" and remote_system.api_key:
            return {
                "name": remote_system.name,
                "api_key": remote_system.api_key.key,
                "bi_id": remote_system.bi_id,
                "enable_fmevent": remote_system.enable_fmevent,
                "enable_metrics": remote_system.enable_metrics,
                "nodata_policy": "C",
                "nodata_ttl": 3600,
                # register_unknown_policy
                "remote_system": str(remote_system.id),
            }
        return {}

    @classmethod
    def clean_reference(cls, remote_system: "RemoteSystem", remote_id: str):
        """Build reference string. Maybe add aliases ?"""
        return f"{REFERENCE_CODE}:{remote_system.name}:{remote_id}"

    @classmethod
    def from_reference(cls, reference: str) -> Tuple["RemoteSystem", str]:
        if not reference.startswith(REFERENCE_CODE):
            raise ValueError("Unknown Reference format")
        _, name, remote_id = reference.split(":")
        rs = RemoteSystem.get_by_name(name)
        if not rs:
            raise ValueError("Unknown Remote System by name %s" % name)
        return rs, remote_id

    def reset_lock(self):
        """"""

    @property
    def has_configured_metrics(self) -> bool:
        """Check configured collected metrics"""
        return self.enable_metrics or self.enable_fmevent

    @classmethod
    def get_metric_config(cls, remote_system: "RemoteSystem"):
        """Return MetricConfig for Target service"""
        enable_fmevent = remote_system.enable_fmevent and remote_system.event_sync_mode == "P"
        if not remote_system.enable_metrics and not enable_fmevent:
            return {}
        return {
            "type": "remote_system",
            "name": remote_system.name,
            "bi_id": remote_system.bi_id,
            "sharding_key": 0,
            "enable_fmevent": remote_system.enable_fmevent,
            "enable_metrics": remote_system.enable_metrics,
            "api_key": remote_system.api_key.key if remote_system.api_key else None,
            "channel": {
                "policy": remote_system.remote_collectors_policy,
                "batch_signal": remote_system.remote_collectors_batch_signal,
                "batch_size": remote_system.metrics_min_batch_size,
                "batch_delay_s": remote_system.metrics_batch_delay,
                "enable_event": enable_fmevent,
                "enable_metrics": remote_system.enable_metrics,
            },
            "rules": [],
            "items": [],
        }

    def push_events(self, events: List[Dict[str, Any]], deferred: List[str]):
        """Push events from Collector"""
        from noc.core.service.loader import get_service

        svc = get_service()
        try:
            events = self.get_handler().get_events(events, deferred)
        except Exception:
            error_report(suppress_log=True)
            return
            # error = str(e)
        if not events:
            return
        max_ts, num = 0, 0
        for num, event in enumerate(sorted(events, key=operator.attrgetter("ts"))):
            max_ts = max(max_ts, event.ts)
            svc.publish(orjson.dumps(event.model_dump()), f"events.{event.target.pool}")
        if max_ts:
            self.last_extract_event = datetime.datetime.fromtimestamp(max_ts)
            RemoteSystem.objects.filter(id=self.id).update(
                last_extract_event=self.last_extract_event,
                last_successful_extract_event=self.last_successful_extract_event,
            )


def processed_remote_event(remote_system: str, events: List[Dict[str, Any]], deferred: List[str]):
    """"""
    rs = RemoteSystem.get_by_name(remote_system)
    if not rs:
        return
    rs.push_events(events, deferred)
