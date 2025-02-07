# ----------------------------------------------------------------------
# Service Instance
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional, List, Iterable, Any

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
    EnumField,
    BinaryField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.ip import IP
from noc.core.resource import from_resource
from noc.core.models.serviceinstanceconfig import InstanceType, ServiceInstanceConfig
from noc.core.models.inputsources import InputSource
from noc.models import get_model_id
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import ServiceSummary
from noc.main.models.pool import Pool

DISCOVERY_SOURCE = InputSource.DISCOVERY
CLIENT_INSTANCE_NAME = "client"

logger = logging.getLogger(__name__)


class AddressItem(EmbeddedDocument):
    pool: "Pool" = PlainReferenceField(Pool, required=False)
    address: str = StringField(required=True)
    address_bin = IntField()
    is_active = BooleanField(default=True)
    sources: List[InputSource] = ListField(EnumField(InputSource))
    # session

    def clean(self):
        self.address_bin = IP.prefix(self.address).d


class ServiceInstance(Document):
    """
    Service Instance.

    Service Instance. Binding Service to
    resource and os process


    Attributes:
        service: Reference to Service
        managed_object: Object for resource bind
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
            "#reference",
            "type",
            "remote_id",
            ("addresses.address_bin", "port"),
            {"fields": ["service", "managed_object", "remote_id", "port"], "unique": True},
            {"fields": ["expires"], "expireAfterSeconds": 0},
        ],
    }
    service = PlainReferenceField("sa.Service", required=True)
    # Instance Description
    type: InstanceType = EnumField(InstanceType, required=True, default=InstanceType.OTHER)
    # ? discriminator
    reference = BinaryField(required=False)
    # Not required/TTL
    # For port services
    managed_object: Optional["ManagedObject"] = ForeignKeyField(ManagedObject, required=False)
    fqdn: str = StringField()
    # Sources that find sensor
    sources: List[InputSource] = ListField(EnumField(InputSource))
    port = IntField(min_value=0, max_value=65536, default=0)
    addresses: List[AddressItem] = EmbeddedDocumentListField(AddressItem)
    # NRI port id, converted by portmapper to native name
    name: str = StringField(required=False)
    macs: List[str] = ListField(StringField(required=True))
    nri_port = StringField()
    # Object id in remote system
    remote_id = StringField()
    # CPE
    resources: List[str] = ListField(StringField(required=False))
    # Operation Attributes
    oper_status: bool = BooleanField()
    oper_status_change = DateTimeField()
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    uptime = FloatField(default=0)
    expires = DateTimeField(required=False)
    # used by
    # weight ?
    # labels ?

    @property
    def interface(self):
        """Return Interface resource"""
        for r in self.resources:
            if r.startswith("if"):
                r, _ = from_resource(r)
                return r
            elif r.startswith("si"):
                r, _ = from_resource(r)
                return r.interface
        return None

    @property
    def address(self) -> Optional[str]:
        """Return first active Address"""
        for a in self.addresses or []:
            if a.is_active:
                return a.address

    @property
    def config(self) -> "ServiceInstanceConfig":
        """Return configuration on type"""
        return ServiceInstanceConfig.get_config(self.type, self.service)

    @property
    def weight(self) -> int:
        """
        Instance weight, by resource.
            * interface/sub - interface profile
            * object - Managed Object Profile
            * alarm - ?
        """
        if self.managed_object:
            return self.managed_object.object_profile.weight
        return 1

    def __str__(self) -> str:
        name = self.name or self.service.label
        if self.type == InstanceType.NETWORK_HOST:
            return f"[{self.type}|{self.macs[0]}] {name}"
        elif self.type == InstanceType.NETWORK_CHANNEL and self.managed_object:
            return f"[{self.type}|{self.managed_object}] {name}"
        elif self.type == InstanceType.NETWORK_CHANNEL and self.remote_id:
            return f"[{self.type}|{self.remote_id}] {name}"
        return f"[{self.type}] {name}"

    def refresh_managed_object(
        self, o: Optional["ManagedObject"] = None, source: Optional[InputSource] = None, bulk=None
    ):
        """
        Update ManagedObject on instance
        Args:
            o: ManagedObject
            source: Update source
            bulk: Update query accumulator
        """
        if not o:
            # Getting managed_object by query
            return
        elif self.managed_object and self.managed_object.id == o.id:
            # Already set
            return
        oo = self.managed_object
        self.managed_object = o
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$set": {"managed_object": o.id}})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(managed_object=o)
            # Update Summary
            ServiceSummary.refresh_object(self.managed_object)
            if oo:
                ServiceSummary.refresh_object(oo)

    def reset_object(self, bulk=None):
        """Clean ManagedObject from Instance"""
        if not self.managed_object:
            return
        oo = self.managed_object
        self.managed_object = None
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$unset": {"managed_object": 1}})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(managed_object=None)
            # Update Summary
            ServiceSummary.refresh_object(oo)

    @classmethod
    def iter_object_instances(cls, managed_object: ManagedObject) -> Iterable["ServiceInstance"]:
        """Iterate over Object Instances"""
        q = Q()
        rds = {}
        if managed_object.remote_system and managed_object.remote_id:
            rds[managed_object.remote_id] = str(managed_object.remote_system)
        for m in managed_object.mappings or []:
            rds[m["remote_id"]] = m["remote_system"]
        if rds:
            q |= Q(remote_id__in=list(rds))
        if managed_object.address:
            q |= Q(addresses__address=managed_object.address)
        for si in ServiceInstance.objects.filter(q):
            if rds and si.remote_id and str(si.service.remote_system.id) != rds.get(si.remote_id):
                continue
            yield si

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
    def get_services_by_alarm(cls, alarm: ActiveAlarm):
        """Getting Service Instance by alarm"""
        q = Q(managed_object=alarm.managed_object.id)
        if alarm.is_link_alarm and getattr(alarm.components, "interface", None):
            q |= Q(resources=alarm.components.interface.as_resource())
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

    def bind_object(
        self,
        o: ManagedObject,
        iface: Optional[Any] = None,
        ts: Optional[str] = None,
    ):
        self.refresh_managed_object(o)
        now = datetime.datetime.now()
        # ? Register Address
        self.last_seen = ts or now

    def unbind_object(self):
        """Remove ManagedObject from ServiceInstance"""
        # Unregister Address

    def register_endpoint(
        self,
        source: InputSource,
        addresses: Optional[List[str]] = None,
        port: Optional[str] = None,
        session: Optional[str] = None,
        pool: Optional[Pool] = None,
        #
        ts: Optional[datetime.datetime] = None,
    ):
        """
        Add endpoint address to instance
        Args:
            source: Source data instance
            addresses: IP Address list
            port: TCP/UDP port number
            session: Register DCS session
            pool: Address pool
            ts: Registered timestamp
        """
        processed = set()
        new_addresses = []
        changed = False
        for a in self.addresses:
            if a.address not in addresses and source in a.sources:
                # Skip
                continue
            elif a.address in addresses and source not in a.sources:
                # Additional source
                a.sources.append(source)
                changed |= True
            new_addresses.append(a)
            processed.add(a.address)
        # New Addresses
        for a in set(addresses) - set(processed):
            new_addresses.append(
                AddressItem(address=a, address_bin=IP.prefix(a).d, sources=[source], pool=pool),
            )
            changed |= True
        self.addresses = new_addresses
        if port and self.port != port:
            changed |= True
            self.port = port
        # Update instance
        self.service.fire_event("seen")
        now = datetime.datetime.now()
        if source == InputSource.DISCOVERY:
            self.last_seen = ts or now
            changed |= True
        return changed

    def deregister_endpoint(
        self,
        source: InputSource,
        session: Optional[str] = None,
        addresses: Optional[List[str]] = None,
    ):
        """Remove endpoint address from instance"""
        address = []
        for a in self.addresses:
            if source in a.sources:
                a.sources.remove(source.value)
            if not a.sources:
                continue
            address.append(a)
        self.addresses = address

    def bind_resource(self, o):
        """Add Resource to ServiceInstance"""
        if not hasattr(o, "as_resource"):
            raise AttributeError("Model %s not Supported Resource Method" % get_model_id(o))
        rid = o.as_resource()
        if rid in self.resources:
            return
        self.resources.append(rid)
        ServiceInstance.objects.filter(id=self.id).update(resources=self.resources)
        if self.managed_object:
            ServiceSummary.refresh_object(self.managed_object)

    def clean_resource(self, code: str):
        """
        Clean resource by Key
        Attrs:
            code: Resource code
        """
        if not self.resources:
            return
        resources = [c for c in self.resources if not c.startswith(code)]
        if len(self.resources) == len(resources):
            return
        self.resources = resources
        ServiceInstance.objects.filter(id=self.id).update(resources=self.resources)
        if self.managed_object:
            ServiceSummary.refresh_object(self.managed_object)

    def update_resources(self, res: List[Any], source: InputSource, bulk=None):
        """
        Update resources for service instance
        Attrs:
            res: Resource list
            source: Source code
            bulk: Bulk update list
        """
        resources = []
        cfg = self.config
        for o in res:
            if not hasattr(o, "as_resource"):
                raise AttributeError("Model %s not Supported Resource Method" % get_model_id(o))
            if hasattr(o, "state") and cfg.send_approve:
                o.fire_event("approved")
            rid = o.as_resource()
            c, _ = rid.split(":", 1)
            if c not in cfg.allow_resources:
                logger.info("Resource not allowed in service instance profile")
                continue
            resources.append(rid)
            logger.info("Binding service %s to interface %s", self.service, o.name)
        self.resources = resources
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$set": {"resources": self.resources}})]
        else:
            ServiceInstance.objects.filter(id=self.id).update(resources=self.resources)
            if self.managed_object:
                ServiceSummary.refresh_object(self.managed_object)

    @classmethod
    def from_config(
        cls,
        service,
        config: ServiceInstanceConfig,
        **kwargs,
    ) -> "ServiceInstance":
        """Create Service Instance"""
        # First discovered
        si = ServiceInstance(
            type=config.type,
            service=service,
            name=kwargs.get("name"),
            fqdn=kwargs.get("fqdn"),
            remote_id=kwargs.get("remote_id"),
            nri_port=kwargs.get("nri_port"),
        )
        if kwargs.get("macs"):
            si.macs = [m for m in kwargs["macs"]]
        return si

    @classmethod
    def get_object_resources(cls, o):
        """Return all resources used by object"""
        return {}
