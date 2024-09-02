# ----------------------------------------------------------------------
# Service Instance
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Iterable

# Third-party modules
from pymongo import UpdateOne
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    DateTimeField,
    FloatField,
    ListField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.ip import IP
from noc.core.resource import from_resource
from noc.models import get_model_id
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool

SOURCES = {"discovery", "etl", "manual"}


class AddressItem(EmbeddedDocument):
    pool: "Pool" = PlainReferenceField(Pool, required=False)
    address: str = StringField(required=True)
    address_bin = IntField()
    is_active = BooleanField(default=True)
    sources: List[str] = ListField(StringField(choices=list(SOURCES)))

    def clean(self):
        self.address_bin = IP.prefix(self.address).d


class ServiceInstance(Document):
    """
    Service Instance.

    Service Instance. Binding Service to
    resource and os process


    Attributes:
        service: Reference to Service
        managed_object: Object for resource binded
        resources: Resource Id List
    """

    meta = {
        "collection": "serviceinstances",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "service",
            "managed_object",
            "addresses.address",
            "resources",
            {"fields": ["service", "managed_object", "remote_id", "port"], "unique": True},
            ("addresses.address_bin", "port"),
        ],
    }
    name: str = StringField(required=True)
    service = PlainReferenceField("sa.Service", required=True)
    # For port services
    managed_object = ForeignKeyField(ManagedObject, required=False)
    fqdn = StringField()
    # ? discriminator
    # Sources that find sensor
    sources = ListField(StringField(choices=list(SOURCES)))
    port = IntField(min_value=0, max_value=65536, default=0)
    addresses: List[AddressItem] = EmbeddedDocumentListField(AddressItem)
    # NRI port id, converted by portmapper to native name
    nri_port = StringField()
    # Object id in remote system
    remote_id = StringField()
    # CPE
    resources: List[str] = ListField(StringField(required=False))
    status: bool = BooleanField()
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    uptime = FloatField(default=0)
    # used by
    # weight ?
    # labels ?

    @property
    def weight(self) -> int:
        """
        Instance weight, by resource.
            * interface/sub - interface profile
            * object - Managed Object Profile
            * alarm - ?
        """
        return 1

    def is_match_alarm(self, alarm: ActiveAlarm) -> bool:
        """Check alarm applying to instance"""
        if self.resources and alarm.is_link_alarm:
            return alarm.components.interface.as_resource() in self.resources
        elif self.managed_object and self.managed_object.id == alarm.managed_object.id:
            return True
        elif self.addresses and "address" in alarm.vars and alarm.vars["address"] == self.address:
            return True
        return False

    @classmethod
    def get_services_by_alarm(cls, alarm: ActiveAlarm) -> List["Service"]:
        """Getting Service Instance by alarm"""
        q = Q(managed_object=alarm.managed_object.id)
        if alarm.is_link_alarm and getattr(alarm.components, "interface", None):
            q |= Q(resources=alarm.components.inteface.as_resource())
        address = None
        if "address" in alarm.vars:
            address = alarm.vars.get("address")
        elif "peer" in alarm.vars:
            # BGP alarms
            address = alarm.vars.get("peer")
        if address:
            q |= Q(addresses__address=address)
        # Name, port
        return ServiceInstance.objects.filter(q).scalar("service")

    def __str__(self) -> str:
        name = self.name or self.service.label
        if self.managed_object:
            return f"{self.managed_object.name} - {name}"
        if self.address:
            return f"{self.address}:{self.port} - {name}"
        return name

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "nri_port" in self._changed_fields:
            pass
        #    self.unbind_interface()

    @property
    def interface(self):
        """Return Interface resource"""
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        for r in self.resources:
            # filter by code ?
            r, _ = from_resource(r)
            if r and isinstance(r, (Interface, SubInterface)):
                return r
        return None

    @property
    def address(self) -> Optional[str]:
        """Return first active Address"""
        if not self.addresses:
            return None
        return self.addresses[0].address

    def seen(
        self,
        source: Optional[str],
        pool: Optional[Pool] = None,
        addresses: Optional[List[str]] = None,
        port: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        """
        Seen Instance
        """
        if source not in self.sources:
            self.sources = list(set(self.sources or []).union({source}))
            self._get_collection().update_one({"_id": self.id}, {"$addToSet": {"sources": source}})
        if port and self.port != port:
            self.port = port
            ServiceInstance.objects(id=self.id).update(port=port)
        if addresses is None:
            return
        new = set(addresses)
        for a in self.addresses:
            if a.address in new and source not in a.sources:
                a.sources.append(source)
            if a.address in new:
                new.remove(a.address)
        for a in new:
            self.addresses.append(
                AddressItem(address=a, address_bin=IP.prefix(a).d, sources=[source], pool=pool),
            )
        ServiceInstance.objects(id=self.id).update(addresses=self.addresses, port=port)
        self.service.fire_event("seen")

    def unseen(self, source: Optional[str] = None):
        """
        Unseen Instance on current source
        """
        if source and source in SOURCES:
            self.sources = list(set(self.sources or []) - {source})
            self._get_collection().update_one({"_id": self.id}, {"$pull": {"sources": source}})
        if not source or not self.sources:
            # For empty source, clean sources
            self._get_collection().delete_one({"_id": self.id})
            # self.sources = []
            # self._get_collection().update_one({"_id": self.id}, {"$set": {"sources": []}})
            # delete

    def set_object(self, o, bulk=None):
        """Set instance ManagedObject instance"""
        if self.managed_object and self.managed_object.id == o.id:
            return
        self.managed_object = o
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$set": {"managed_object": o.id}})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(managed_object=o)

    def add_resource(self, o, bulk=None):
        """Add Resource to ServiceInstance"""
        if not hasattr(o, "as_resource"):
            raise AttributeError("Model %s not Supported Resource Method" % get_model_id(o))
        rid = o.as_resource()
        if rid in self.resources:
            return
        self.resources.append(rid)
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$addToSet": {"resources": rid}})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(resources=self.resources)

    def clean_resource(self, code: str, bulk=None):
        """Clean resource by Key"""
        if not self.resources:
            return
        resources = [c for c in self.resources if not c.startswith(code)]
        if len(self.resources) == len(resources):
            return
        self.resources = resources
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$set": resources})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(resources=self.resources)

    @classmethod
    def iter_object_instances(cls, managed_object: ManagedObject) -> Iterable["ServiceInstance"]:
        q = Q(managed_object=managed_object.id)
        if managed_object.remote_system and managed_object.remote_id:
            q |= Q(remote_id=managed_object.remote_id)
        if managed_object.address:
            q |= Q(addresses__address=managed_object.address)
        for si in ServiceInstance.objects.filter(q):
            yield si

    @classmethod
    def get_object_resources(cls, o):
        """Return all resources used by object"""
