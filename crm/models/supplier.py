# ----------------------------------------------------------------------
# Supplier
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, BooleanField, LongField
import cachetools

# NOC modules
from .supplierprofile import SupplierProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.wf.models.state import State
from noc.project.models.project import Project
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@workflow
@on_delete_check(check=[("phone.PhoneRange", "supplier")])
class Supplier(Document):
    meta = {
        "collection": "noc.suppliers",
        "indexes": ["name"],
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField()
    description = StringField()
    is_affilated = BooleanField(default=False)
    profile = PlainReferenceField(SupplierProfile)
    state = PlainReferenceField(State)
    project = ForeignKeyField(Project)
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

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Supplier.objects.filter(id=id).first()

    @classmethod
    def can_set_label(cls, label):
        if label.enable_supplier:
            return True
        return False
