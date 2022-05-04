# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from typing import List
import datetime
from threading import Lock

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    DateTimeField,
    LongField,
    IntField,
    ReferenceField,
    DictField,
)
import cachetools

# NOC modules
from .slaprofile import SLAProfile
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.sa.models.service import Service
from noc.pm.models.agent import Agent
from noc.main.models.label import Label
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync
from noc.core.wf.decorator import workflow

PROBE_TYPES = IGetSLAProbes.returns.element.attrs["type"].choices

id_lock = Lock()
_target_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@Label.model
@change
@bi_sync
@workflow
class SLAProbe(Document):
    meta = {
        "collection": "noc.sla_probes",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object", "labels", "effective_labels"],
    }

    managed_object = ForeignKeyField(ManagedObject)
    agent = PlainReferenceField(Agent)
    # Probe name (<managed object>, <group>, <name> triple must be unique
    name = StringField()
    # Probe profile
    profile = PlainReferenceField(SLAProfile, default=SLAProfile.get_default_profile)
    # Probe group (Owner)
    group = StringField()
    # Optional description
    description = StringField()
    state = PlainReferenceField(State)
    # Timestamp of last seen
    last_seen = DateTimeField()
    # Timestamp expired
    expired = DateTimeField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Probe type
    type = StringField(choices=[(x, x) for x in PROBE_TYPES])
    #
    tos = IntField(min=0, max=64)
    # IP address or URL, depending on type
    target = StringField()
    # Hardware timestamps
    hw_timestamp = BooleanField(default=False)
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    extra_labels = DictField()
    #
    service = ReferenceField(Service)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return SLAProbe.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return SLAProbe.objects.filter(bi_id=id).first()

    def clean(self):
        if self.extra_labels:
            self.labels += [
                ll
                for ll in Label.merge_labels(self.extra_labels.values())
                if SLAProbe.can_set_label(ll)
            ]

    @cachetools.cached(_target_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_target(self):
        address = self.target
        if ":" in address:
            # port
            address, port = self.target.split(":")
        print("Search address", address)
        # @todo SubInterface search
        mo = ManagedObject.objects.filter(address=address)[:1]
        if mo:
            return mo[0]
        return None

    @classmethod
    def iter_effective_labels(self, probe: "SLAProbe") -> List[str]:
        return probe.labels + probe.profile.labels

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_slaprobe")
