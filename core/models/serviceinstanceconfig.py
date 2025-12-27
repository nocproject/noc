# ----------------------------------------------------------------------
# Service Instances Typing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional, Any, List, ClassVar, Type

# Third-party modules
from mongoengine.queryset.visitor import Q

# NOC Modules
from noc.core.models.valuetype import ValueType
from noc.core.validators import is_fqdn, is_ipv4


class InstanceType(enum.Enum):
    """
    Description Instance Type of Service
    * process - OS Process instance
    * network_device - network client device, CPE, MAC Address?
    * network_port - network switch port, Channel service interface, subinterface; remote_system, nri_port
    * endpoint - l3 endpoint, IP Address (ManagedObject) - Port
    * other - Other Scenario, (Configured Based)
    """

    # OS_PROCESS = "process"  # OS Process: ManagedObject, Name (pid)
    ASSET = "asset"
    NETWORK_CHANNEL = "network"
    SERVICE_ENDPOINT = "endpoint"
    SERVICE_CLIENT = "client"
    OTHER = "other"


@dataclass
class ServiceInstanceTypeConfig:
    allow_resources: Optional[List[str]] = None
    allow_manual: bool = False
    # For multiple object, control TTL ?
    only_one_instance: bool = True
    send_approve: bool = False
    allow_register: bool = False
    ttl: Optional[int] = None
    refs_caps: Optional[Any] = None
    asset_group: Optional[Any] = None


@dataclass
class ServiceInstanceConfig:
    """
    Instance Configuration.
    Source describe Instance, and create by it.
    Config + Settings (from profile) -> Instance
    """

    type: ClassVar[InstanceType]
    name: str
    managed_object: Optional[Any] = None
    remote_id: Optional[str] = None
    nri_port: Optional[str] = None
    fqdn: Optional[str] = None
    addresses: List[str] = None
    services: List[str] = None
    port: int = 0
    asset_refs: List[str] = None

    @classmethod
    def get_type(cls, i_type: InstanceType) -> Type["ServiceInstanceConfig"]:
        """Return Config instance by type"""
        match i_type:
            case InstanceType.ASSET:
                cfg = NetworkHostInstance
            case InstanceType.NETWORK_CHANNEL:
                cfg = NetworkChannelInstance
            case InstanceType.SERVICE_ENDPOINT:
                cfg = ServiceEndPoint
            case InstanceType.SERVICE_CLIENT:
                cfg = ConfigInstance
            case _:
                cfg = ConfigInstance
        return cfg

    @classmethod
    def from_settings(
        cls,
        settings: "ServiceInstanceTypeConfig",
        service,
        name: Optional[str] = None,
    ) -> List["ServiceInstanceConfig"]:
        """Create Config from settings"""
        raise NotImplementedError()

    @classmethod
    def from_config(
        cls,
        name: Optional[str] = None,
        fqdn: Optional[str] = None,
        **kwargs,
    ):
        return cls(
            name=name,
            fqdn=fqdn,
            addresses=kwargs.get("addresses"),
            port=kwargs.get("port"),
            remote_id=kwargs.get("remote_id"),
            nri_port=kwargs.get("nri_port"),
            asset_refs=kwargs.get("asset_refs"),
            services=kwargs.get("services"),
        )

    def get_queryset(self, service: Any, settings: ServiceInstanceTypeConfig, **kwargs) -> Q:
        """Request ServiceInstance QuerySet"""
        if not settings.only_one_instance:
            # SourceETL, On Discovery - ManagedObject
            return Q(
                service=service, type=self.type, name=self.name or None, remote_id=self.remote_id
            )
        return Q(service=service, type=self.type, name=self.name or None)


class NetworkHostInstance(ServiceInstanceConfig):
    type = InstanceType.ASSET

    @classmethod
    def from_group(cls, group) -> List["NetworkHostInstance"]:
        from noc.inv.models.resourcegroup import ResourceGroup

        r = []
        for o in ResourceGroup.get_objects_from_expression(group, "sa.ManagedObject"):
            r.append(cls.from_config(o.name, managed_object=o))
        return r

    @classmethod
    def from_settings(
        cls,
        settings: "ServiceInstanceTypeConfig",
        service,
        name: Optional[str] = None,
    ) -> List["NetworkHostInstance"]:
        """Create Config from settings"""
        if settings.asset_group and settings.asset_group.id in service.effective_client_groups:
            return cls.from_group(settings.asset_group)
        if not settings.refs_caps:
            return []
        hostname, refs = None, []
        for c in service.iter_caps():
            if c.capability == settings.refs_caps:
                refs += c.capability.get_references(c.value)
            # More Complex: Service - get_hostname ?
            if c.capability.type == ValueType.HOSTNAME:
                hostname = c.value
        if not refs:
            return []
        # Fqdn
        cfg = cls.from_config(name=name, asset_refs=refs, fqdn=hostname)
        return [cfg]


class NetworkChannelInstance(ServiceInstanceConfig):
    """Describe Network port bind Service, defined by port name on Managed Object"""

    type = InstanceType.NETWORK_CHANNEL

    @classmethod
    def from_settings(
        cls,
        settings: "ServiceInstanceTypeConfig",
        service,
        name: Optional[str] = None,
    ) -> List["ServiceInstanceConfig"]:
        """Create Config from settings"""
        caps = service.get_caps()
        if not settings.refs_caps or settings.refs_caps.name not in caps:
            return []
        refs = settings.refs_caps.get_references(caps[settings.refs_caps.name])
        addresses = []
        if settings.refs_caps.type in [ValueType.IPV4_ADDR, ValueType.IP_ADDR]:
            if settings.refs_caps.multi:
                addresses = caps[settings.refs_caps.name]
            else:
                addresses = [caps[settings.refs_caps.name]]
        elif not refs:
            return []
        if settings.only_one_instance:
            cfg = cls.from_config(name=name, asset_refs=refs, addresses=addresses or None)
            return [cfg]
        r = []
        for c in caps[settings.refs_caps.name]:
            refs = settings.refs_caps.get_references(c)
            if name:
                cfg = cls.from_config(name=f"{c}@{name}", asset_refs=refs)
            else:
                cfg = cls.from_config(name=f"{c}@", asset_refs=refs)
            r.append(cfg)
        return r


class ServiceEndPoint(ServiceInstanceConfig):
    """Describe OS Process, that running service tasks. Defined by name and ManagedObject Group"""

    type = InstanceType.SERVICE_ENDPOINT

    @classmethod
    def from_settings(
        cls,
        settings: "ServiceInstanceTypeConfig",
        service,
        name: Optional[str] = None,
    ) -> List["ServiceInstanceConfig"]:
        """
        Create Config from settings
        """
        caps = service.get_caps()
        refs_caps = settings.refs_caps
        if not refs_caps or refs_caps.name not in caps or refs_caps.type != ValueType.HTTP_URL:
            return []
        refs = refs_caps.get_references(caps[refs_caps.name])
        if not refs:
            return []
        url = urlparse(refs[0].split("::")[1])
        host, *port = url.netloc.split(":")
        addressed, fqdn = None, None
        if is_ipv4(host):
            addressed = [host]
        elif is_fqdn(host):
            fqdn = host
        if port:
            port = int(port[0])
        cfg = cls.from_config(
            name=name,
            fqdn=fqdn,
            asset_refs=refs,
            addresses=addressed,
            port=port,
        )
        return [cfg]


class ConfigInstance(ServiceInstanceConfig):
    type = InstanceType.OTHER

    @classmethod
    def from_settings(
        cls,
        settings: "ServiceInstanceTypeConfig",
        service,
        name: Optional[str] = None,
    ) -> List["ServiceInstanceConfig"]:
        """Create Config from settings"""
        caps = service.get_caps()
        if not settings.refs_caps or settings.refs_caps.name not in caps:
            return []
        refs = settings.refs_caps.get_references(caps[settings.refs_caps.name])
        if not refs:
            return []
        cfg = cls.from_config(name=name, asset_refs=refs)
        return [cfg]

    # Handler ?
