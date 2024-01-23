# ----------------------------------------------------------------------
# Address Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from functools import partial
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.main.models.template import Template
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@on_delete_check(
    check=[
        ("ip.Address", "profile"),
        ("sa.ManagedObjectProfile", "address_profile_interface"),
        ("sa.ManagedObjectProfile", "address_profile_management"),
        ("sa.ManagedObjectProfile", "address_profile_dhcp"),
        ("sa.ManagedObjectProfile", "address_profile_neighbor"),
        ("sa.ManagedObjectProfile", "address_profile_confdb"),
    ]
)
class AddressProfile(Document):
    meta = {"collection": "addressprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    # Address workflow
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "ip.Address")
    )
    style = ForeignKeyField(Style)
    # Template.subject to render Address.name
    name_template = ForeignKeyField(Template)
    # Template.subject to render Address.fqdn
    fqdn_template = ForeignKeyField(Template)
    # Send seen event to prefix
    seen_propagation_policy = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="D")
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_WORKFLOW_NAME = "Default Resource"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AddressProfile"]:
        return AddressProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return AddressProfile.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["AddressProfile"]:
        return AddressProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_addressprofile")
