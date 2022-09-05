# ----------------------------------------------------------------------
# Workflow model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging
from typing import Optional

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ReferenceField, LongField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.main.models.remotesystem import RemoteSystem

logger = logging.getLogger(__name__)
id_lock = Lock()
_default_state_cache = cachetools.TTLCache(maxsize=1000, ttl=1)


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
        ("sla.SLAProfile", "workflow"),
        ("inv.SensorProfile", "workflow"),
        ("inv.InterfaceProfile", "workflow"),
        ("vc.VPNProfile", "workflow"),
        ("vc.VLANProfile", "workflow"),
        ("vc.L2DomainProfile", "workflow"),
    ]
)
class Workflow(Document):
    meta = {"collection": "workflows", "strict": False, "auto_create_index": False}
    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
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

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["Workflow"]:
        return Workflow.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["Workflow"]:
        return Workflow.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["Workflow"]:
        return Workflow.objects.filter(name=name).first()

    @classmethod
    def get_default_workflow(cls, model_id):
        from noc.models import get_model

        model = get_model(model_id)
        workflow = getattr(model, "DEFAULT_WORKFLOW_NAME", cls.DEFAULT_WORKFLOW_NAME)
        return Workflow.get_by_name(workflow)

    @cachetools.cached(_default_state_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_default_state(self):
        from .state import State

        return State.objects.filter(workflow=self.id, is_default=True).first()

    def set_default_state(self, state):
        from .state import State

        logger.info("[%s] Set default state to: %s", self.name, state.name)
        for s in State.objects.filter(workflow=self.id):
            if s.is_default and s.id != state.id:
                logger.info("[%s] Removing default status from: %s", self.name, s.name)
                s.is_default = False
                s.save()
        # Invalidate caches
        key = str(self.id)
        if key in _default_state_cache:
            try:
                del _default_state_cache[key]
            except KeyError:
                pass
