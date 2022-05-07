# ----------------------------------------------------------------------
# ManagedObject Json GrafanaDS models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Union, Dict, List, Literal, Any

# Third-party modules
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

# NOC modules
from noc.aaa.models.user import User
from noc.main.models.label import Label
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.interface import Interface
from ..models.jsonds import RangeSection

MAX_MANAGED_OBJECT_RESPONSE = 2000


# Query
class QueryPayloadItem(BaseModel):
    managed_object: int
    interface: Optional[str]

    @property
    def expr(self) -> str:
        return f"managed_object={self.managed_object}"


# Variable
class VariablePayloadItem(BaseModel):
    target: Optional[str]
    managed_object: Optional[Union[str, int]]
    labels: Optional[List[str]] = None
    interface_profile: Optional[str] = None
    administrative_domain: Optional[str] = None

    @property
    def mo(self):
        if not self.managed_object:
            return None
        return ManagedObject.get_by_bi_id(self.managed_object)


class ManagedObjectTarget(BaseModel):
    target: Literal["managed_object"]
    labels: Optional[List[str]] = None
    administrative_domain: Optional[str] = None


class InterfaceTarget(BaseModel):
    target: Literal["interface"]
    managed_object: int
    interface_profile: Optional[str] = None
    type: str = "physical"

    @property
    def mo(self):
        if not self.managed_object:
            return None
        return ManagedObject.get_by_bi_id(self.managed_object)


class InterfaceProfileTarget(BaseModel):
    target: Literal["interface_profile"]


VariableRequestItem = Union[ManagedObjectTarget, InterfaceTarget, InterfaceProfileTarget]


class VariableRequest(BaseModel):
    payload: Dict[str, Any]
    range: RangeSection = None

    @staticmethod
    def var_default():
        # Labels
        return [
            {"__text": ll, "__value": ll}
            for ll in Label.objects.filter(enable_managedobject=True).values_list("name")
        ]

    @staticmethod
    def var_managed_object(payload: "ManagedObjectTarget", user: "User" = None):
        mos = ManagedObject.objects.filter(is_managed=True)
        if payload.labels:
            mos = mos.filter(effective_labels__overlap=payload.labels)
        if not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        return [
            {"__text": f"{name} ({address})", "__value": bi_id}
            for bi_id, address, name in mos.values_list("bi_id", "address", "name")[
                :MAX_MANAGED_OBJECT_RESPONSE
            ]
        ]

    @staticmethod
    def var_interface(payload: "InterfaceTarget", user: "User" = None):
        ifaces = Interface.objects.filter(managed_object=payload.mo, type="physical")
        profiles = payload.interface_profile
        if isinstance(profiles, str):
            profiles = [profiles]
        if profiles:
            ifaces = ifaces.filter(profile__in=profiles)
        return [
            {
                "__text": f"{iface.name} status: {iface.status} ({iface.description})",
                "__value": iface.name,
            }
            for iface in ifaces
        ]

    @staticmethod
    def var_interface_profile(payload: "InterfaceProfileTarget", user: "User" = None):
        if not user.is_superuser and payload.mo not in UserAccess.get_domains(user):
            raise HTTPException(
                status_code=404, detail=f"User has no access to ManagedObject: {payload.mo}"
            )
        return [
            {"__text": ip.name, "__value": str(ip.id)}
            for ip in set(
                ip
                for ip in Interface.objects.filter(
                    managed_object=payload.mo, type=payload.type
                ).values_list("profile")
            )
        ]

    @staticmethod
    def var_test_variables(*args, **kwargs):
        return [
            {"__text": "Device1#59565", "__value": "2083341664757472739"},
            {"__text": "Device2#59609", "__value": "272411249935345586"},
            {"__text": "Device3#8328", "__value": "825392260101847512"},
            {"__text": "Device4", "__value": "3780187837837487731"},
        ]

    def get_variable_keys(self):
        return [{"type": "managed_object", "text": "ManagedObject"}, {"type": "", "text": "Labels"}]
