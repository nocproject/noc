# ----------------------------------------------------------------------
# ResourceGroup model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import threading

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField
import cachetools

# NOC modules
from noc.config import config
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.datastream.decorator import datastream
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from .technology import Technology

id_lock = threading.Lock()


@Label.model
@bi_sync
@datastream
@on_delete_check(
    check=[
        ("inv.ResourceGroup", "parent"),
        # sa.ManagedObject
        ("sa.ManagedObject", "static_service_groups"),
        ("sa.ManagedObject", "effective_service_groups"),
        ("sa.ManagedObject", "static_client_groups"),
        ("sa.ManagedObject", "effective_client_groups"),
        # sa.ManagedObjectSelector
        ("sa.ManagedObjectSelector", "filter_service_group"),
        ("sa.ManagedObjectSelector", "filter_client_group"),
        # phone.PhoneRange
        ("phone.PhoneRange", "static_service_groups"),
        ("phone.PhoneRange", "effective_service_groups"),
        ("phone.PhoneRange", "static_client_groups"),
        ("phone.PhoneRange", "effective_client_groups"),
        # phone.PhoneNumber
        ("phone.PhoneNumber", "static_service_groups"),
        ("phone.PhoneNumber", "effective_service_groups"),
        ("phone.PhoneNumber", "static_client_groups"),
        ("phone.PhoneNumber", "effective_client_groups"),
    ]
)
class ResourceGroup(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """

    meta = {"collection": "resourcegroups", "strict": False, "auto_create_index": False}

    # Group | Name
    name = StringField()
    technology = PlainReferenceField(Technology)
    parent = PlainReferenceField("inv.ResourceGroup")
    description = StringField()
    # @todo: FM integration
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s (%s)" % (self.name, self.technology.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ResourceGroup.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return ResourceGroup.objects.filter(bi_id=id).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_resourcegroup:
            yield "resourcegroup", self.id

    @property
    def has_children(self):
        return bool(ResourceGroup.objects.filter(parent=self.id).only("id").first())

    @classmethod
    def can_set_label(cls, label):
        if label.enable_resourcegroup:
            return True
        return False
