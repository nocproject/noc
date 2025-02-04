# ----------------------------------------------------------------------
# VLAN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import random
import datetime
from threading import Lock
from typing import Optional, Set, Union, Iterable, List, Tuple, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    IntField,
    DateTimeField,
)
from mongoengine.errors import ValidationError, NotUniqueError
import cachetools

# NOC modules
from .vlanprofile import VLANProfile
from .l2domain import L2Domain
from .vlanfilter import VLANFilter
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_save, on_delete_check

id_lock = Lock()

FREE_VLAN_STATE = "Free"
FULL_VLAN_RANGE = set(range(1, 4096))


@Label.model
@bi_sync
@workflow
@on_save
@on_delete_check(check=[("ip.Prefix", "vlan")])
class VLAN(Document):
    meta = {
        "collection": "vlans",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["l2_domain", "vlan"], "unique": True},
            "expired",
            "labels",
            "effective_labels",
        ],
    }

    name = StringField(default="")
    profile = PlainReferenceField(
        VLANProfile, required=True, default=VLANProfile.get_default_profile
    )
    vlan = IntField(min_value=1, max_value=4095)
    l2_domain = PlainReferenceField(L2Domain, required=True)
    description = StringField()
    state = PlainReferenceField(State)
    project = ForeignKeyField(Project)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Discovery integration
    # Timestamp when object first discovered
    first_discovered = DateTimeField()
    # Timestamp when object last seen by discovery
    last_seen = DateTimeField()
    # Timestamp when send "expired" event
    expired = DateTimeField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return f"{self.l2_domain}:{self.vlan} ({self.name})"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VLAN"]:
        return VLAN.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["VLAN"]:
        return VLAN.objects.filter(bi_id=bi_id).first()

    @classmethod
    def get_component(cls, managed_object, vlan=None, **kwargs) -> Optional["VLAN"]:
        if not vlan:
            return
        if managed_object.l2_domain:
            return VLAN.objects.filter(l2_domain=managed_object.l2_domain, vlan=int(vlan)).first()

    @property
    def resource_key(self):
        return self.vlan

    @property
    def resource_domain(self):
        return self.l2_domain

    @classmethod
    def get_resource_keys(
        cls,
        domain: L2Domain,
        vlan_filter: Optional[VLANFilter] = None,
        keys: Optional[List[int]] = None,
        strategy: str = "L",
        exclude_keys: Optional[Iterable[int]] = None,
        limit: int = 1,
        **kwargs,
    ) -> List[int]:
        """Generate Non-used vlan keys"""
        vlans: Set[int] = set(keys or []) or FULL_VLAN_RANGE
        if vlan_filter:
            vlans &= set(vlan_filter.include_vlans)
        if vlan_filter and vlan_filter.exclude_vlans:
            vlans -= set(vlan_filter.exclude_vlans)
        if exclude_keys:
            vlans -= exclude_keys
        # logger.debug("[%s] Getting Resource Keys: %s", self, vlans)
        # Check pool in VLAN
        free_states = list(State.objects.filter(name=FREE_VLAN_STATE).values_list("id"))
        occupied_vlans = VLAN.objects.filter(l2_domain=domain, state__nin=free_states).scalar(
            "vlan"
        )
        vlans -= set(occupied_vlans)
        if strategy == "L":
            return sorted(vlans, reverse=True)[:limit]
        elif strategy == "F":
            return sorted(vlans)[:limit]
        return random.choices(list(vlans), k=limit)

    @classmethod
    def iter_resources_by_key(
        cls,
        keys: Iterable[int],
        domain: L2Domain,
        allow_create: bool = False,
    ) -> Iterable[Tuple[int, Optional["VLAN"], Optional[str]]]:
        """
        Iterate resource over requested keys
        Args:
            keys: List keys for ensure
            domain: L2Domain
            allow_create: Allow create key if not exists
        """
        processed = set()
        for vlan in VLAN.objects.filter(l2_domain=domain, vlan__in=keys):
            yield vlan.vlan, vlan, None
            processed.add(vlan.vlan)
        # Create new record ? to resource class
        for key in set(keys) - processed:
            record = cls.from_template(vlan_id=key, l2_domain=domain)
            if not allow_create:
                yield key, record, None
                continue
            error = None
            try:
                # ? save to outside allocated ?
                record.save()
            except ValidationError as e:
                record, error = None, f"Validation error when saving record: {e}"
            except NotUniqueError as e:
                record, error = None, f"VLAN not unique: {e}"
            yield key, record, error

    # def clean(self):
    #     super().clean()
    #     if not hasattr(self, "_changed_fields") or "l2_domain" in self._changed_fields:
    #         if self.vlan not in set(self.l2_domain.get_effective_vlan_id()):
    #             raise ValidationError(f"VLAN {self.vlan} not in allowed {self.l2_domain} range")

    def reserve(
        self,
        allocated_till: Optional[datetime.datetime] = None,
        user: Optional[Any] = None,
        confirm: bool = True,
        reservation_id: Optional[str] = None,
    ):
        """
        Set record As reserve
        Args:
            allocated_till:
        """
        # self.allocated_till = allocated_till
        # self.allocated_user = user
        # self.tt = reservation_id
        self.fire_event("reserve")
        if confirm:
            self.fire_event("approve")

    @classmethod
    def from_template(
        cls,
        vlan_id: int,
        l2_domain: L2Domain,
        name: Optional[str] = None,
    ) -> "VLAN":
        """Create VLAN from Template"""
        vlan = VLAN(
            vlan=vlan_id,
            name=name or f"VLAN {vlan_id:04d}",
            l2_domain=l2_domain,
            profile=l2_domain.get_default_vlan_profile(),
            description="",
        )
        if name:
            vlan.name = name
        return vlan

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vlan")
