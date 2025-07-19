# ----------------------------------------------------------------------
# Service Instances Typing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Optional, Any, List, ClassVar

# Third-party modules
from mongoengine.queryset.visitor import Q


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
    OTHER = "other"


@dataclass
class ServiceInstanceTypeConfig:
    allow_resources: Optional[List[str]] = None
    allow_manual: bool = False
    # For multiple object, control TTL ?
    only_one_instance: bool = True
    send_approve: bool = False
    allow_register: bool = False


@dataclass
class ServiceInstanceConfig:
    type: ClassVar[InstanceType]
    name: str
    # managed_object: Optional[Any] = None ?
    remote_id: Optional[str] = None
    nri_port: Optional[str] = None
    fqdn: Optional[str] = None
    addresses: List[str] = None
    port: int = 0
    asset_refs: List[str] = None

    # type
    @classmethod
    def get_config(
        cls,
        i_type: InstanceType,
        name: Optional[str] = None,
        **kwargs,
    ) -> "ServiceInstanceConfig":
        """Return Config instance by type"""
        match i_type:
            case InstanceType.ASSET:
                cfg = NetworkHostInstance
            case InstanceType.NETWORK_CHANNEL:
                cfg = NetworkChannelInstance
            case InstanceType.SERVICE_ENDPOINT:
                cfg = ServiceEndPont
            case _:
                cfg = ConfigInstance
        return cfg(
            name=name,
            fqdn=kwargs.get("fqdn"),
            addresses=kwargs.get("addresses"),
            port=kwargs.get("port"),
            remote_id=kwargs.get("remote_id"),
            nri_port=kwargs.get("nri_port"),
            asset_refs=kwargs.get("asset_refs"),
        )

    def get_queryset(self, service: Any, **kwargs) -> Q:
        """Request ServiceInstance QuerySet"""
        return Q(service=service, type=self.type, name=self.name or None)


class NetworkHostInstance(ServiceInstanceConfig):
    type = InstanceType.ASSET


class NetworkChannelInstance(ServiceInstanceConfig):
    """Describe Network port bind Service, defined by port name on Managed Object"""

    type = InstanceType.NETWORK_CHANNEL


class ServiceEndPont(ServiceInstanceConfig):
    """Describe OS Process, that running service tasks. Defined by name and ManagedObject Group"""

    type = InstanceType.SERVICE_ENDPOINT


class ConfigInstance(ServiceInstanceConfig):
    type = InstanceType.OTHER
