# ----------------------------------------------------------------------
# Agent
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import enum
from threading import Lock
from typing import Optional, List, Iterable, Union

# Third-party modules
from bson import ObjectId
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    LongField,
    ListField,
    EmbeddedDocumentListField,
    EnumField,
    DateTimeField,
    ReferenceField,
)
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.wf.decorator import workflow
from noc.core.change.decorator import change
from noc.core.caps.decorator import capabilities
from noc.core.etl.remotemappings import mappings
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.remotemappingsitem import RemoteMappingItem
from noc.inv.models.capsitem import CapsItem
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject
from noc.config import config
from .agentprofile import AgentProfile

id_lock = Lock()


class AgentType(enum.Enum):
    NOC_AGENT = "noc_agent"
    GUFO_AGENT = "gufo_agent"
    ZABBIX_AGENT = "zabbix_agent"
    TELEGRAF = "telegraf"
    OTHER = "other"
    AUTO = "auto"


class AgentIp(EmbeddedDocument):
    ip = StringField()

    def __str__(self):
        return self.ip


class AgentMAC(EmbeddedDocument):
    mac = StringField()

    def __str__(self):
        return self.mac


def gen_key() -> str:
    """
    Generate unique key
    :return:
    """
    import secrets
    import base64

    while True:
        # Generate key
        seed = secrets.token_bytes(20)
        key = base64.b32encode(seed).decode("utf-8")
        # Check for uniqueness
        if not Agent.objects.filter(key=key).first():
            return key


@workflow
@change
@bi_sync
@Label.model
@capabilities
@mappings
@on_delete_check(
    check=[("sa.Service", "agent"), ("inv.Sensor", "agent"), ("sla.SLAProbe", "agent")],
    clean=[("sa.DiscoveredObject", "agent")],
)
class Agent(Document):
    meta = {
        "collection": "agents",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["serial", "ip.ip", "mac.mac", "labels", "effective_labels"],
    }

    name = StringField(unique=True)
    description = StringField()
    profile: AgentProfile = PlainReferenceField(
        AgentProfile, default=AgentProfile.get_default_profile
    )
    type: AgentType = EnumField(AgentType, default=AgentType.AUTO)
    zk_check_interval = IntField()
    managed_object: Optional["ManagedObject"] = ForeignKeyField(ManagedObject, required=False)
    # Agent identification
    # Auto-updated if profile.update_addresses is set
    serial = StringField()
    ip: List[AgentIp] = EmbeddedDocumentListField(AgentIp)
    port: Optional[int] = IntField(min_value=1000, max_value=65536, required=False)
    fqdn: str = StringField(required=False)
    mac: List[AgentMAC] = EmbeddedDocumentListField(AgentMAC)
    # Workflow
    state = PlainReferenceField(State)
    # Last state change
    state_changed = DateTimeField()
    last_metric_update = DateTimeField()
    # Capabilities
    caps: List[CapsItem] = EmbeddedDocumentListField(CapsItem)
    # Unique secret authentication key
    key = StringField(unique=True, default=gen_key)
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Remote Mappings
    mappings: List[RemoteMappingItem] = EmbeddedDocumentListField(RemoteMappingItem)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Agent"]:
        return Agent.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Agent"]:
        return Agent.objects.filter(bi_id=bi_id).first()

    def get_effective_check_interval(self) -> int:
        if self.zk_check_interval:
            return self.zk_check_interval
        return self.profile.zk_check_interval

    def _invalidate_cache(self):
        with id_lock:
            self._id_cache[self.id] = self
            self._id_cache[str(self.id)] = self
            self._bi_id_cache[self.bi_id] = self

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmetricstarget:
            yield "cfgmetricstarget", f"pm.Agent::{self.bi_id}"

    def update_addresses(
        self,
        serial: Optional[str] = None,
        mac: Optional[List[str]] = None,
        ip: Optional[List[str]] = None,
    ) -> None:
        changed = False
        if self.serial != serial:
            self.serial = serial
            changed = True
        if mac:
            if sorted(mac) != sorted(x.mac for x in self.mac):
                self.mac = [AgentMAC(mac=x) for x in sorted(mac)]
                changed = True
        if ip:
            if sorted(ip) != sorted(x.ip for x in self.ip):
                self.ip = [AgentIp(ip=x) for x in sorted(ip)]
                changed = True
        if changed:
            self.save()
            self._invalidate_cache()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_agent")

    @property
    def auth_level(self) -> int:
        """
        Get current authorization level
        :return:
        """
        if "noc::agent::auth::auth" in self.effective_labels:
            return 2
        if "noc::agent::auth::pre" in self.effective_labels:
            return 1
        return 0

    @classmethod
    def iter_effective_labels(cls, instance: "Agent") -> Iterable[List[str]]:
        yield list(instance.labels or [])
        state = instance.state or instance.profile.workflow.get_default_state()
        if state.labels:
            yield list(state.labels)

    @property
    def has_configured_metrics(self) -> bool:
        """Check configured collected metrics"""
        state = self.state or self.profile.workflow.get_default_state()
        return state.is_productive

    @classmethod
    def get_metric_config(cls, agent: "Agent"):
        """Return MetricConfig for Target service"""
        from noc.inv.models.sensor import Sensor

        if not agent.state.is_productive:
            return {}
        r = {
            "type": "agent",
            "name": agent.name,
            "bi_id": agent.bi_id,
            "mapping_refs": [f"name:{agent.name.lower()}"],
            "addresses": [],
            "sharding_key": agent.bi_id,
            "managed_object": None,
            "enable_fmevent": False,
            "enable_metrics": True,
            "api_key": agent.key,
            "exposed_labels": Label.build_expose_labels(agent.effective_labels, "expose_metric"),
            "labels": [],
            "rules": [],
            "sensors": [],
        }
        if agent.managed_object:
            r["managed_object"] = agent.managed_object.bi_id
        for m in agent.iter_remote_mappings():
            r["mapping_refs"].append(RemoteSystem.clean_reference(m.remote_system, m.remote_id))
        for a in agent.ip or []:
            r["addresses"].append(a.ip)
        for s in Sensor.objects.filter(agent=agent):
            cfg = Sensor.get_metric_config(s)
            if cfg:
                r["sensors"].append(cfg)
        return r
