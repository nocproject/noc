# ----------------------------------------------------------------------
# Service Instances Typing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from hashlib import sha512
from typing import Optional, Any, List

# Third-party modules
from pydantic import BaseModel
from mongoengine.queryset.visitor import Q


class Status(enum.IntEnum):
    UNKNOWN = 0
    UP = 1
    SLIGHTLY_DEGRADED = 2
    DEGRADED = 3
    DOWN = 4


class InstanceType(enum.Enum):
    """
    Description Instance Type of Service
    * process - OS Process instance
    * network_device - network client device
    * network_port - network switch port
    * endpoint - l3 endpoint
    """

    # OS_PROCESS = "process"  # OS Process: ManagedObject, Name (pid)
    NETWORK_HOST = "network_host"  # ? CPE, MAC Address
    NETWORK_CHANNEL = (
        "network_channel"  # Channel service interface, subinterface; remote_system, nri_port
    )
    SERVICE_ENDPOINT = "endpoint"  # IP Address (ManagedObject) - Port
    OTHER = "other"  # Other Scenario (Configured Based)


class ServiceInstanceConfig(BaseModel):
    type: InstanceType
    required_fields: List[str]
    allow_resources: Optional[List[str]] = None
    allow_manual: bool = False
    # For multiple object, control TTL ?
    only_one_object: bool = True
    send_approve: bool = False

    def get_reference(self, service: Any) -> bytes:
        """Calculate unique Reference"""
        return sha512(str(service.id).encode("utf-8")).digest()[:10]

    def get_queryset(self, service: str, **kwargs) -> Q:
        """Request ServiceInstance QuerySet"""
        return Q(type=self.type, service=service)

    @classmethod
    def get_config(cls, type: InstanceType, service) -> "ServiceInstanceConfig":
        """Return Config instance by type"""
        if type == InstanceType.NETWORK_HOST:
            return NetworkHostInstance()
        elif type == InstanceType.NETWORK_CHANNEL:
            return NetworkChannelInstance()
        elif type == InstanceType.SERVICE_ENDPOINT:
            return ServiceEndPont()


class NetworkHostInstance(ServiceInstanceConfig):
    """NetworkHost Instance, Describe Network host or CPE, defined by MAC Address"""

    type: InstanceType = InstanceType.NETWORK_HOST
    required_fields = ["mac"]

    def get_reference(self, service: Any, **kwargs) -> bytes:
        return sha512(self.mac.encode("utf-8")).digest()[:10]

    def get_queryset(self, service: str, **kwargs) -> Q:
        return Q(type=self.type, macs__mac=kwargs["macs"])


class NetworkChannelInstance(ServiceInstanceConfig):
    """Describe Network port bind Service, defined by port name on Managed Object"""

    type: InstanceType = InstanceType.NETWORK_CHANNEL
    required_fields = ["managed_object"]

    def get_reference(self, service: Any) -> bytes:
        reference = f"{self.managed_object.id}:{self.resources[0]}"
        return sha512(reference.encode("utf-8")).digest()[:10]

    def get_queryset(self, service: str, **kwargs) -> Q:
        q = Q()
        # By Group Resource Group
        if kwargs.get("remote_id"):
            # OR
            # Remote System
            q |= Q(service=service, type=self.type, remote_id=kwargs["remote_id"])
        if self.only_one_object:
            # self.only_one_object
            q |= Q(service=service, type=self.type)
        elif kwargs.get("managed_object"):
            q |= Q(service=service, type=self.type, managed_object=kwargs["managed_object"])
        return q


class ServiceEndPont(ServiceInstanceConfig):
    """Describe OS Process, that running service tasks. Defined by name and ManagedObject Group"""

    type: InstanceType = InstanceType.SERVICE_ENDPOINT

    def get_reference(self, service: Any) -> bytes:
        reference = f"{self.addresses[0]}:{self.port}"
        return sha512(reference.encode("utf-8")).digest()[:10]

    def get_queryset(self, service: str, **kwargs) -> Q:
        # By Group and allow_one_object
        return Q(service=service, type=self.type, name=kwargs["name"])
