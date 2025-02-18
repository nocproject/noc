# ----------------------------------------------------------------------
# Service Instances Typing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from hashlib import sha512
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
class ServiceInstanceConfig:
    """Service Instance type configuration"""

    type: ClassVar[InstanceType]
    required_fields: ClassVar[List[str]]
    allow_resources: Optional[List[str]] = None
    allow_manual: bool = False
    # For multiple object, control TTL ?
    only_one_object: bool = True
    send_approve: bool = False

    def get_reference(self, service: Any) -> bytes:
        """Calculate unique Reference"""
        return sha512(f"{self.type}:{service.id}".encode("utf-8")).digest()[:10]

    def get_queryset(self, service: Any, **kwargs) -> Q:
        """Request ServiceInstance QuerySet"""
        return Q(type=self.type, service=service)

    @classmethod
    def get_config(cls, type: InstanceType, service) -> "ServiceInstanceConfig":
        """Return Config instance by type"""
        match type:
            case InstanceType.ASSET:
                cfg = NetworkHostInstance()
            case InstanceType.NETWORK_CHANNEL:
                cfg = NetworkChannelInstance()
            case InstanceType.SERVICE_ENDPOINT:
                cfg = ServiceEndPont()
            case _:
                cfg = ConfigInstance()
        if service.profile.instance_policy_settings:
            p = service.profile.instance_policy_settings
            if p.instance_type != type:
                pass
            cfg.allow_manual = p.allow_manual
            cfg.only_one_object = p.only_one_object
            cfg.allow_resources = list(p.allow_resources)
            cfg.send_approve = p.send_approve
        return cfg


class NetworkHostInstance(ServiceInstanceConfig):
    """NetworkHost Instance, Describe Network host or CPE, defined by MAC Address"""

    type = InstanceType.ASSET
    required_fields = ["mac"]
    only_one_object = True

    def get_reference(self, service: Any, macs=None, **kwargs) -> bytes:
        return sha512(macs[0].encode("utf-8")).digest()[:10]

    def get_queryset(self, service: str, macs=None, **kwargs):
        return Q(type=self.type, macs__in=macs)


class NetworkChannelInstance(ServiceInstanceConfig):
    """Describe Network port bind Service, defined by port name on Managed Object"""

    type = InstanceType.NETWORK_CHANNEL
    required_fields = ["managed_object"]

    def get_queryset(self, service: str, managed_object=None, remote_id=None, **kwargs):
        q = Q()
        # By Group Resource Group
        if remote_id:
            # OR
            # Remote System
            q |= Q(service=service, type=self.type, remote_id=remote_id)
        if self.only_one_object:
            # self.only_one_object
            q |= Q(service=service, type=self.type)
        elif managed_object:
            q |= Q(service=service, type=self.type, managed_object=managed_object)
        return q


class ServiceEndPont(ServiceInstanceConfig):
    """Describe OS Process, that running service tasks. Defined by name and ManagedObject Group"""

    type = InstanceType.SERVICE_ENDPOINT

    def get_queryset(self, service: str, name=None, **kwargs):
        # By Group and allow_one_object
        return Q(service=service, type=self.type, name=name)


class ConfigInstance(ServiceInstanceConfig):
    type = InstanceType.OTHER
