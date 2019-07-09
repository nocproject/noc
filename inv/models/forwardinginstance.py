# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Forwarding Instance model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.core.model.decorator import on_delete_check


@on_delete_check(ignore=[("inv.SubInterface", "forwarding_instance")])
@six.python_2_unicode_compatible
class ForwardingInstance(Document):
    """
    Non-default forwarding instances
    """

    meta = {
        "collection": "noc.forwardinginstances",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object"],
    }
    managed_object = ForeignKeyField(ManagedObject)
    type = StringField(
        choices=[(x, x) for x in ("ip", "bridge", "VRF", "VPLS", "VLL")], default="ip"
    )
    virtual_router = StringField(required=False)
    name = StringField()
    # VRF/VPLS
    rd = StringField(required=False)

    def __str__(self):
        return "%s: %s" % (self.managed_object.name, self.name if self.name else "default")

    def delete(self, *args, **kwargs):
        # Delete subinterfaces
        for si in self.subinterface_set.all():
            si.delete()
        # Delete forwarding instance
        super(ForwardingInstance, self).delete(*args, **kwargs)

    @property
    def subinterface_set(self):
        # Avoid circular references
        from .subinterface import SubInterface

        return SubInterface.objects.filter(forwarding_instance=self.id)
