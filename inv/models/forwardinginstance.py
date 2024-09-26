# ---------------------------------------------------------------------
# Forwarding Instance model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check
from noc.config import config


@change(audit=False)
@on_delete_check(ignore=[("inv.SubInterface", "forwarding_instance")])
class ForwardingInstance(Document):
    """
    Non-default forwarding instances
    """

    meta = {
        "collection": "noc.forwardinginstances",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object", "name"],
    }
    managed_object = ForeignKeyField(ManagedObject)
    type = StringField(
        choices=[(x, x) for x in ("table", "bridge", "vrf", "vll", "vpls", "evpn", "vxlan")],
        default="table",
    )
    virtual_router = StringField(required=False)
    name = StringField()
    # VRF/VPLS
    vpn_id = StringField(required=False)
    rd = StringField(required=False)
    rt_export = ListField(StringField(required=False))
    rt_import = ListField(StringField(required=False))

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name if self.name else "default")

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ForwardingInstance"]:
        return ForwardingInstance.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            yield "managedobject", self.managed_object.id

    def delete(self, *args, **kwargs):
        # Delete subinterfaces
        for si in self.subinterface_set.all():
            si.delete()
        # Delete forwarding instance
        super().delete(*args, **kwargs)

    @property
    def subinterface_set(self):
        # Avoid circular references
        from .subinterface import SubInterface

        return SubInterface.objects.filter(forwarding_instance=self.id)
