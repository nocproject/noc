# ----------------------------------------------------------------------
# ManagedObject Json GrafanaDS models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Union, List, Literal

# Third-party modules
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

# NOC modules
from noc.aaa.models.user import User
from noc.main.models.label import Label
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.interface import Interface

MAX_MANAGED_OBJECT_RESPONSE = 2000


# Query
class QueryPayloadItem(BaseModel):
    managed_object: int
    interface: Optional[str]

    @property
    def expr(self) -> str:
        return f"managed_object={self.managed_object}"


# Variable
class LabelTarget(BaseModel):
    target: Literal["", "labels"]

    def get_variables(self, user: "User" = None):
        # Labels
        return [
            {"__text": ll, "__value": ll}
            for ll in Label.objects.filter(allow_models=["sa.ManagedObject"]).values_list("name")
        ]


class ManagedObjectTarget(BaseModel):
    target: Literal["managed_object"]
    labels: Optional[List[str]] = None
    administrative_domain: Optional[str] = None

    def get_variables(self, user: "User" = None):
        mos = ManagedObject.objects.filter(is_managed=True)
        if self.labels:
            mos = mos.filter(effective_labels__overlap=self.labels)
        if not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        return [
            {"__text": f"{name} ({address})", "__value": bi_id}
            for bi_id, address, name in mos.values_list("bi_id", "address", "name")[
                :MAX_MANAGED_OBJECT_RESPONSE
            ]
        ]


class InterfaceTarget(BaseModel):
    target: Literal["interface"]
    managed_object: int
    name: Optional[str] = None
    interface_profile: Optional[str] = None
    type: str = "physical"

    @property
    def mo(self):
        if not self.managed_object:
            return None
        return ManagedObject.get_by_bi_id(self.managed_object)

    def get_variables(self, user: "User" = None):
        ifaces = Interface.objects.filter(managed_object=self.mo, type="physical")
        profiles = self.interface_profile
        if isinstance(profiles, str):
            profiles = profiles.strip("()").split("|")
        if profiles:
            ifaces = ifaces.filter(profile__in=profiles)
        return [
            {
                "__text": f"{iface.name} status: {iface.status} ({iface.description})",
                "__value": iface.name,
            }
            for iface in ifaces
        ]


class TestTarget(BaseModel):
    target: Literal["test"]

    @classmethod
    def get_variables(cls, user: "User" = None):
        return [
            {"__text": "Device1#59565", "__value": "2083341664757472739"},
            {"__text": "Device2#59609", "__value": "272411249935345586"},
            {"__text": "Device3#8328", "__value": "825392260101847512"},
            {"__text": "Device4", "__value": "3780187837837487731"},
        ]


class InterfaceProfileTarget(BaseModel):
    target: Literal["interface_profile"]
    managed_object: Optional[int] = None

    @property
    def mo(self) -> Optional[ManagedObject]:
        if not self.managed_object:
            return None
        return ManagedObject.get_by_bi_id(self.managed_object)

    def get_variables(self, user: "User" = None):
        if not user.is_superuser and self.mo.id not in UserAccess.get_domains(user):
            raise HTTPException(
                status_code=404, detail=f"User has no access to ManagedObject: {self.mo}"
            )
        return [
            {"__text": ip.name, "__value": str(ip.id)}
            for ip in set(
                ip
                for ip in Interface.objects.filter(
                    managed_object=self.mo, type="physical"
                ).values_list("profile")
            )
        ]


VariablePayloadItem = Union[
    LabelTarget, ManagedObjectTarget, InterfaceTarget, InterfaceProfileTarget, TestTarget
]
