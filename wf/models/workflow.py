# ----------------------------------------------------------------------
# Workflow model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from threading import Lock
import operator
import logging
from typing import Optional, Dict, Any, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    LongField,
    ListField,
    UUIDField,
)
import cachetools

# NOC modules
from noc.models import get_model
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.main.models.remotesystem import RemoteSystem

from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

logger = logging.getLogger(__name__)
id_lock = Lock()
_default_state_cache = cachetools.TTLCache(maxsize=1000, ttl=1)
_wiping_state_cache = cachetools.TTLCache(maxsize=1000, ttl=1)


@bi_sync
@change
@on_delete_check(
    check=[
        ("wf.State", "workflow"),
        ("wf.Transition", "workflow"),
        ("ip.AddressProfile", "workflow"),
        ("ip.PrefixProfile", "workflow"),
        ("crm.SubscriberProfile", "workflow"),
        ("crm.SupplierProfile", "workflow"),
        ("phone.PhoneNumberProfile", "workflow"),
        ("phone.PhoneRangeProfile", "workflow"),
        ("pm.AgentProfile", "workflow"),
        ("sa.ServiceProfile", "workflow"),
        ("sa.ManagedObjectProfile", "workflow"),
        ("sa.ObjectDiscoveryRule", "workflow"),
        ("sla.SLAProfile", "workflow"),
        ("inv.CPEProfile", "workflow"),
        ("inv.SensorProfile", "workflow"),
        ("inv.InterfaceProfile", "workflow"),
        ("vc.VPNProfile", "workflow"),
        ("vc.VLANProfile", "workflow"),
        ("vc.L2DomainProfile", "workflow"),
    ]
)
class Workflow(Document):
    meta = {
        "collection": "workflows",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "wf.workflows",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    is_active = BooleanField()
    description = StringField()
    #
    allowed_models = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    DEFAULT_WORKFLOW_NAME = "Default"

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _wiping_states_cache = cachetools.TTLCache(maxsize=100, ttl=900)

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "$collection": self._meta["json_collection"],
            "description": self.description,
        }
        if self.is_active:
            r["is_active"] = self.is_active
        if self.allowed_models:
            r["allowed_models"] = list(self.allowed_models)
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "uuid",
                "$collection",
                "is_active",
                "description",
                "allowed_models",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Workflow"]:
        return Workflow.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Workflow"]:
        return Workflow.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["Workflow"]:
        return Workflow.objects.filter(name=name).first()

    @classmethod
    def get_default_workflow(cls, model_id):
        from noc.models import get_model

        workflow = Workflow.objects.filter(allowed_models__in=[model_id]).first()
        if workflow:
            return workflow
        model = get_model(model_id)
        workflow = getattr(model, "DEFAULT_WORKFLOW_NAME", cls.DEFAULT_WORKFLOW_NAME)
        return Workflow.get_by_name(workflow)

    @cachetools.cached(_default_state_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_default_state(self):
        from .state import State

        return State.objects.filter(workflow=self.id, is_default=True).first()

    @cachetools.cached(_wiping_state_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_wiping_state(self):
        from .state import State

        return State.objects.filter(workflow=self.id, is_wiping=True).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_wiping_states_cache"), lock=lambda _: id_lock)
    def get_wiping_states(cls, model: Optional[str] = None):
        from .state import State

        w_states = State.objects.filter(is_wiping=True)
        if model:
            wfs = list(Workflow.objects.filter(allowed_models__in=[model]).scalar("id"))
            w_states = w_states.filter(workflow__in=wfs)
        return [s.id for s in w_states]

    def set_wiping_state(self, state):
        from .state import State

        logger.info("[%s] Set wiping state to: %s", self.name, state.name)
        for s in State.objects.filter(workflow=self.id):
            if s.is_wiping and s.id != state.id:
                logger.info("[%s] Removing wiping status from: %s", self.name, s.name)
                s.is_wiping = False
        State.objects.filter(workflow=self.id, is_wiping=True, id__ne=state.id).update(is_wiping=False)
        # Invalidate caches
        key = str(self.id)
        if key in _wiping_state_cache:
            try:
                del _wiping_state_cache[key]
            except KeyError:
                pass

    def set_default_state(self, state):
        from .state import State

        logger.info("[%s] Set default state to: %s", self.name, state.name)
        for s in State.objects.filter(workflow=self.id):
            if s.is_default and s.id != state.id:
                logger.info("[%s] Removing default status from: %s", self.name, s.name)
                s.is_default = False
        State.objects.filter(workflow=self.id, is_default=True, id__ne=state.id).update(is_default=False)
        # Invalidate caches
        key = str(self.id)
        if key in _default_state_cache:
            try:
                del _default_state_cache[key]
            except KeyError:
                pass

    def clean(self):
        for mid in self.allowed_models:
            try:
                get_model(mid)
            except AssertionError:
                raise ValueError(f"Unknown model_id: {mid}")
