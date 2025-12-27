# ----------------------------------------------------------------------
# Service Instance
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional, List, Iterable, Any, Dict, Tuple

# Third-party modules
from pymongo import UpdateOne, ReadPreference
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
    ObjectIdField,
    EmbeddedDocumentListField,
)
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.ip import IP
from noc.core.resource import from_resource
from noc.core.models.serviceinstanceconfig import (
    InstanceType,
    ServiceInstanceConfig,
    ServiceInstanceTypeConfig,
)
from noc.core.models.inputsources import InputSource
from noc.core.models.valuetype import ValueType
from noc.core.validators import is_ipv4, is_fqdn
from noc.core.model.decorator import on_save
from noc.core.checkers.base import Check
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


@on_save
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
            "asset_refs",
            "resources",
            "#reference",
            "type",
            "remote_id",
            "dependencies",
            ("managed_object", "resources"),
            ("asset_refs", "type"),
            ("addresses.address_bin", "port"),
            {"fields": ["service", "type", "managed_object", "remote_id", "name"], "unique": True},
            {"fields": ["expires"], "expireAfterSeconds": 0},
        ],
    }
    service = PlainReferenceField("sa.Service", required=True)
    # Instance Description
    type: InstanceType = EnumField(InstanceType, required=True, default=InstanceType.OTHER)
    name: str = StringField(required=False)
    # Sources that approved data
    sources: List[InputSource] = ListField(EnumField(InputSource))
    # Object
    managed_object: Optional["ManagedObject"] = ForeignKeyField(ManagedObject, required=False)
    # For ETL services, Object id in remote system
    remote_id = StringField()
    # NRI port id, converted by portmapper to native name
    nri_port = StringField()
    # ? discriminator
    reference = BinaryField(required=False)
    # Endpoint Data
    fqdn: str = StringField()
    addresses: List[AddressItem] = EmbeddedDocumentListField(AddressItem)
    port = IntField(min_value=0, max_value=65536, default=0)
    # Asset Data
    asset_refs: List[str] = ListField(StringField(required=True))
    # Used Resources
    resources: List[str] = ListField(StringField(required=True))
    # Service Dependencies
    dependencies: List[str] = ListField(ObjectIdField(required=True))
    # Operation Attributes
    oper_status: bool = BooleanField()
    oper_status_change = DateTimeField()
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    uptime = FloatField(default=0)
    # Not required/TTL
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
            if r.startswith("si"):
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
    def config(self) -> "ServiceInstanceTypeConfig":
        """Return configuration on type"""
        cfg = self.service.profile.get_instance_config(self.type, self.name)
        return cfg or ServiceInstanceTypeConfig()

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
        if self.type == InstanceType.ASSET:
            return f"[{self.type}|{','.join(self.asset_refs)}] {name}"
        if self.type == InstanceType.NETWORK_CHANNEL and self.managed_object:
            return f"[{self.type}|{self.managed_object}] {name}"
        if self.type == InstanceType.NETWORK_CHANNEL and self.remote_id:
            return f"[{self.type}|{self.remote_id}] {name}"
        return f"[{self.type}] {name}"

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "asset_refs" in self._changed_fields:
            ServiceInstance.refresh_local_network_instances([self])

    @classmethod
    def ensure_instance(
        cls,
        service,
        cfg: ServiceInstanceConfig,
        settings: Optional[ServiceInstanceTypeConfig] = None,
    ) -> Optional["ServiceInstance"]:
        """ """
        settings = settings or ServiceInstanceTypeConfig()
        qs = cfg.get_queryset(service, settings)
        instance = ServiceInstance.objects.filter(qs).first()
        logger.debug("[%s] Find Instance by query: %s, Result: %s", service.id, qs, instance)
        if not instance:
            logger.info("[%s] Create new Instance: %s", service.id, cfg.type)
            instance = ServiceInstance.from_config(service, cfg)
            instance.save()
        return instance

    @classmethod
    def from_config(
        cls,
        service,
        config: ServiceInstanceConfig,
        **kwargs,
    ) -> "ServiceInstance":
        """Create Service Instance"""
        # First discovered
        return ServiceInstance(
            type=config.type,
            service=service,
            name=config.name,
            fqdn=config.fqdn,
            remote_id=config.remote_id,
            nri_port=config.nri_port,
            asset_refs=config.asset_refs,
        )

    def update_config(self, cfg: ServiceInstanceConfig):
        """Update instance Data from config"""
        if self.asset_refs != cfg.asset_refs:
            self.asset_refs = cfg.asset_refs
        if self.fqdn != cfg.fqdn:
            self.fqdn = cfg.fqdn

    def seen(
        self,
        source: InputSource,
        last_seen: Optional[datetime.datetime] = None,
        dry_run: bool = False,
    ):
        """Update source"""
        if source not in self.sources:
            self.sources += [source]
        if source not in [InputSource.MANUAL, InputSource.CONFIG]:
            self.last_seen = last_seen or datetime.datetime.now().replace(microsecond=0)
            self.service.fire_event("seen")
            self.expires = None
        # resource Seen
        if not dry_run:
            ServiceInstance.objects.filter(id=self.id).update(
                sources=self.sources,
                last_seen=self.last_seen,
                expires=self.expires,
            )

    def unseen(self, source: InputSource, dry_run: bool = False, force: bool = False):
        """Remove from source"""
        if source in self.sources:
            self.sources.remove(source)
        if dry_run:
            return
        if not self.sources and self.config.ttl and not force:
            self.expires = self.expires or datetime.datetime.now() + datetime.timedelta(
                seconds=self.config.ttl
            )
            ServiceInstance.objects.filter(id=self.id).update(
                sources=self.sources, expires=self.expires
            )
        elif not self.sources:
            # For empty source, clean sources
            ServiceInstance.objects.filter(id=self.id).delete()
        else:
            # Clean Source, ETL - Remove Remote_id, NRI Port, Addresses
            ServiceInstance.objects.filter(id=self.id).update(sources=self.sources)

    def refresh_managed_object(self, o: Optional["ManagedObject"] = None, bulk=None):
        """
        Update ManagedObject on instance
        Args:
            o: ManagedObject
            bulk: Update query accumulator
        """
        if not o:
            # Getting managed_object by query
            return
        if self.managed_object and self.managed_object.id == o.id:
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
        from noc.inv.models.subinterface import SubInterface

        q = Q()
        rds = {}
        for m in managed_object.iter_remote_mappings():
            rds[m.remote_id] = m.remote_system.id
        if rds:
            q |= Q(remote_id__in=list(rds))
        addrs = set()
        if managed_object.address:
            addrs.add(managed_object.address)
        for ipv4_addrs in (
            SubInterface.objects.filter(
                managed_object=managed_object.id, ipv4_addresses__exists=True, enabled_afi="IPv4"
            )
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .scalar("ipv4_addresses")
        ):
            addrs |= {IP.prefix(x).address for x in ipv4_addrs}
        if addrs:
            q |= Q(addresses__address__in=addrs)
        # get_full_fqdn
        q |= Q(fqdn=managed_object.name.lower().strip())
        # Capability Reference
        refs = []
        for c in managed_object.iter_caps():
            refs += c.capability.get_references(c.value)
        if refs:
            q |= Q(asset_refs__in=refs)
        for si in ServiceInstance.objects.filter(q).read_preference(
            ReadPreference.SECONDARY_PREFERRED
        ):
            # By configuration
            if (
                si.remote_id in rds
                and si.service.remote_system
                and si.service.remote_system.id != rds.get(si.remote_id)
            ):
                continue
            yield si

    def is_match_alarm(
        self,
        alarm: ActiveAlarm,
        include_object: bool = False,
    ) -> bool:
        """Check alarm applying to instance"""
        if include_object and alarm.managed_object and self.managed_object != alarm.managed_object:
            return False
        resources = alarm.components.get_resources()
        if resources and frozenset(resources).intersection(self.resources):
            return True
        addresses = self.get_alarm_addresses(alarm)
        if addresses and frozenset(self.address).intersection(addresses):
            return True
        return True

    @classmethod
    def get_alarm_reference(cls, alarm: "ActiveAlarm") -> List[str]:
        """"""
        r = []
        if "mac" in alarm.vars:
            r += [ValueType.MAC_ADDRESS.clean_reference(alarm.vars["mac"])]
        elif "url" in alarm.vars and not is_fqdn(alarm.vars["url"]):
            r += [ValueType.HTTP_URL.clean_reference(alarm.vars["url"])]
        return r

    @classmethod
    def get_alarm_addresses(cls, alarm: "ActiveAlarm") -> List[str]:
        """Convert Active Alarm to addresses"""
        r = []
        # Alarm Class Vars ?
        for vars_name in ["address", "peer"]:
            if vars_name in alarm.vars and is_ipv4(alarm.vars[vars_name]):
                r.append(IP.prefix(alarm.vars[vars_name]).address)
        return r

    @classmethod
    def get_instance_filter_by_alarm(
        cls, alarm: ActiveAlarm, include_object: bool = False
    ) -> Optional[Q]:
        """Build Alarm filter for query affected instances"""
        # Instance | Save include managed object Global | Local reference
        if include_object and alarm.managed_object:
            q = Q(managed_object=alarm.managed_object.id, type=InstanceType.ASSET)
        else:
            q = Q()
        # Resources
        resources = alarm.components.get_resources()
        if resources:
            # Interface, Sub, Peer
            q |= Q(resources=resources)
        try:
            refs = cls.get_alarm_reference(alarm=alarm)
            if refs:
                q |= Q(asset_refs__in=refs)
        except ValueError as e:
            logger.error("[%s] Error converted reference for alarm: %s", alarm.id, str(e))
        # FQDN
        if "url" in alarm.vars and is_fqdn(alarm.vars["url"]):
            q |= Q(fqdn=alarm.vars["url"])
        # Addresses
        addresses = cls.get_alarm_addresses(alarm)
        if addresses:
            q |= Q(addresses__address__in=addresses)
        # Local Name
        if not alarm.managed_object:
            return q or None
        return q or None

    @classmethod
    def get_services_by_alarm(cls, alarm: ActiveAlarm, include_object: bool = False):
        """Getting Service Instance by alarm"""
        q = cls.get_instance_filter_by_alarm(alarm, include_object)
        if not q:
            return []
        return list(ServiceInstance.objects.filter(q).scalar("service"))

    def register_endpoint(
        self,
        source: InputSource,
        addresses: Optional[List[str]] = None,
        port: Optional[str] = None,
        session: Optional[str] = None,
        pool: Optional[Pool] = None,
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
        addresses = addresses or []
        changed = False
        for a in self.addresses:
            if a.address not in addresses and source in a.sources:
                # Skip
                continue
            if a.address in addresses and source not in a.sources:
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
        if InputSource == InputSource.DISCOVERY:
            self.seen(source, last_seen=ts)
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
                a.sources.remove(source)
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

    def update_resources(
        self,
        res: List[Any],
        source: InputSource,
        update_ts: Optional[datetime.datetime] = None,
        bulk=None,
    ):
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
            if not o:
                # Bad resource value.
                continue
            if not hasattr(o, "as_resource"):
                raise AttributeError("Model %s not Supported Resource Method" % get_model_id(o))
            if hasattr(o, "state") and cfg.send_approve:
                o.fire_event("approved")
            rid = o.as_resource()
            c, _ = rid.split(":", 1)
            if c not in (cfg.allow_resources or []):  # has_resource
                logger.warning("Resource not allowed in service instance profile")
                continue
            resources.append(rid)
            if rid not in self.resources:
                logger.info("Binding service %s to interface %s", self.service, o.name)
        if resources and set(self.resources) == set(resources):
            # Not changed - Update only last seen
            self.seen(source, last_seen=update_ts)
            return
        if resources:
            # Update last seen and not save (save on bulk)
            self.seen(source, last_seen=update_ts, dry_run=bool(bulk))
        else:
            self.unseen(source)
        self.resources = resources
        if not self.sources:
            # Instance Deleted
            return
        if bulk is not None:
            bulk += [
                UpdateOne(
                    {"_id": self.id},
                    {
                        "$set": {
                            "resources": self.resources,
                            "sources": [s.value for s in self.sources],
                            "last_seen": self.last_seen,
                        }
                    },
                )
            ]
        else:
            ServiceInstance.objects.filter(id=self.id).update(
                resources=self.resources,
                sources=self.sources,
                last_seen=self.last_seen,
            )
            if self.managed_object and bulk is None:
                ServiceSummary.refresh_object(self.managed_object)

    @classmethod
    def get_object_resources(cls, oid: int) -> Dict[str, Tuple[str, int, str]]:
        """Return all resources used by object"""
        r = {}
        # Secondary Preferred
        coll = ServiceInstance._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED,
        )
        for row in coll.aggregate(
            [
                {"$match": {"managed_object": oid, "resources": {"$exists": True, "$ne": []}}},
                {"$project": {"service": 1, "resources": 1}},
                {
                    "$lookup": {
                        "from": "noc.services",
                        "let": {"i_service": "$service"},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$_id", "$$i_service"]}}},
                            {"$project": {"profile": 1, "bi_id": 1}},
                        ],
                        "as": "svc",
                    }
                },
                {"$unwind": "$svc"},
            ]
        ):
            if not row["svc"]:
                continue
            for rid in row["resources"]:
                _, rid = rid.split(":")
                r[rid] = (row["service"], row["svc"]["bi_id"], row["svc"]["profile"])
        return r

    @classmethod
    def refresh_local_network_instances(cls, instances: Optional[List] = None):
        """"""
        from noc.inv.models.interface import Interface

        ref_mac_instance: Dict[str, ServiceInstance] = {}
        bulk = []
        for si in ServiceInstance.objects.filter(
            type=InstanceType.NETWORK_CHANNEL,
            asset_refs__exists=True,
            asset_refs__ne=[],
        ):
            for r in si.asset_refs or []:
                ref, value = r.split("::", 1)
                if ref == "mac":
                    ref_mac_instance[value] = si
        # Find Interfaces
        for iface in Interface.objects.filter(mac__in=list(ref_mac_instance)):
            if iface.mac not in ref_mac_instance:
                continue
            si = ref_mac_instance.pop(iface.mac)
            si.update_resources([iface], source=InputSource.DISCOVERY, bulk=bulk)
        for si in ref_mac_instance.values():
            si.unseen(source=InputSource.DISCOVERY)
        coll = ServiceInstance._get_collection()
        logger.info("Updated Local Instances: %s", len(bulk))
        if bulk:
            coll.bulk_write(bulk)

    def get_checks(self) -> List[Check]:
        """Getting check for instance. For multiple - applied Any? policy"""
        # Update instance status
        if not self.config.checks:
            return []
        r = []
        for name in self.config.checks:
            r.append(Check(name=name, address=self.address, port=self.port))
        return r
