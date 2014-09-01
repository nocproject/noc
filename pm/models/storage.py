## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (ListField, EmbeddedDocumentField,
                                StringField, BooleanField, IntField)


class CollectorProtocol(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    address = StringField()
    port = IntField()
    protocol = StringField()
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return "%s:%s %s" % (self.address, self.port, self.protocol)


class AccessProtocol(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    protocol = StringField()
    base_url = StringField()
    is_active = BooleanField(default=True)

    def __unicode__(self):
        return self.base_url


class Storage(Document):
    meta = {
        "collection": "noc.pm.storages",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    description = StringField(required=False)
    type = StringField()
    collectors = ListField(EmbeddedDocumentField(CollectorProtocol))
    access = ListField(EmbeddedDocumentField(AccessProtocol))

    def __unicode__(self):
        return self.name

    @property
    def default_collector(self):
        """
        Returns tuple of (address, port, protocol) of first active
        collector. Returns None if no default collector set
        """
        for c in self.collectors:
            if c.is_active:
                return c.address, c.port, c.protocol
        return None
