# ----------------------------------------------------------------------
# AgentProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union
from functools import partial

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mongo.fields import PlainReferenceField
from noc.wf.models.workflow import Workflow

id_lock = Lock()


@on_delete_check(check=[("pm.Agent", "profile")])
class AgentProfile(Document):
    meta = {"collection": "agentprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    zk_check_interval = IntField(default=60)
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "pm.AgentProfile")
    )
    update_addresses = BooleanField(default=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Agent Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AgentProfile"]:
        return AgentProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "AgentProfile":
        sp = AgentProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = AgentProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            sp.save()
        return sp
