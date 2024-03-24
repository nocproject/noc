# ----------------------------------------------------------------------
# Agent
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Iterable, Union

# Third-party modules
from bson import ObjectId
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, LongField, ListField, EmbeddedDocumentField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.core.wf.decorator import workflow
from noc.main.models.label import Label
from noc.wf.models.state import State
from .agentprofile import AgentProfile

id_lock = Lock()


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
@bi_sync
@Label.model
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
    profile = PlainReferenceField(AgentProfile, default=AgentProfile.get_default_profile)
    zk_check_interval = IntField()
    # Agent identification
    # Auto-updated if profile.update_addresses is set
    serial = StringField()
    ip = ListField(EmbeddedDocumentField(AgentIp))
    mac = ListField(EmbeddedDocumentField(AgentMAC))
    # Workflow
    state = PlainReferenceField(State)
    # Unique secret authentication key
    key = StringField(unique=True, default=gen_key)
    #
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

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
            if list(sorted(mac)) != list(sorted(x.mac for x in self.mac)):
                self.mac = [AgentMAC(mac=x) for x in sorted(mac)]
                changed = True
        if ip:
            if list(sorted(ip)) != list(sorted(x.ip for x in self.ip)):
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
        if instance.state.labels:
            yield list(instance.state.labels)
