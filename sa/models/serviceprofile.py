# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ReferenceField, DictField,
                                IntField, BooleanField, ListField,
                                EmbeddedDocumentField)
## NOC modules
from servicetype import ServiceType
from noc.crm.models.supplier import Supplier


class ServiceDependencyRule(EmbeddedDocument):
    # Dependency group name
    name = StringField()
    # All members of type
    type = ReferenceField(ServiceType)
    # Minimal configured services
    min_services = IntField()
    # Maximal configured servuces
    max_services = IntField()
    # Fault can be propagated to this dependency group
    propagate_fault = BooleanField(default=True)
    # When set, minimal amount of OK services
    # which can block fault propagation
    min_ok = IntField()


class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles"
    }

    name = StringField(unique=True)
    description = StringField()
    type = ReferenceField(ServiceType, required=True)
    # Jinja2 template to render service label
    label_template = StringField()
    data = DictField()
    default_supplier = ReferenceField(Supplier)
    default_state = IntField()
    # Customer Facing Service/Resource Facing Service
    direction = StringField(
        choices=[
            ("C", "CFS"),
            ("R", "RFS")
        ],
        default="C"
    )
    dependencies = ListField(EmbeddedDocumentField(ServiceDependencyRule))
    # Maximum objects can be bound to server
    bind_limit = IntField(default=0)

    def __unicode__(self):
        return self.name

    def create_service(self, **kwargs):
        from service import Service

        kw = kwargs.copy()
        kw["profile"] = self
        kw["direction"] = self.direction
        svc = Service(**kw)
        svc.save()
        return svc
