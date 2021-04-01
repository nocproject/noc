# ---------------------------------------------------------------------
# SLA Probe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ListField
import cachetools

# NOC modules
from .slaprofile import SLAProfile
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.label import Label
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


PROBE_TYPES = IGetSLAProbes.returns.element.attrs["type"].choices

id_lock = Lock()
_target_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@Label.model
class SLAProbe(Document):
    meta = {
        "collection": "noc.sla_probes",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object"],
    }

    managed_object = ForeignKeyField(ManagedObject)
    # Probe name (<managed object>, <group>, <name> triple must be unique
    name = StringField()
    # Probe profile
    profile = PlainReferenceField(SLAProfile)
    # Probe group
    group = StringField()
    # Optional description
    description = StringField()
    # Probe type
    type = StringField(choices=[(x, x) for x in PROBE_TYPES])
    # IP address or URL, depending on type
    target = StringField()
    # Hardware timestamps
    hw_timestamp = BooleanField(default=False)
    # Optional tags
    labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return SLAProbe.objects.filter(id=id).first()

    @cachetools.cached(_target_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_target(self):
        mo = ManagedObject.objects.filter(address=self.target)[:1]
        if mo:
            return mo[0]
        return None

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_slaprobe")
