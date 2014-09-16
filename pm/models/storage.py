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
    is_selectable = BooleanField(default=True)

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

    ALL = "all"
    PRIORITY = "pri"
    ROUNDROBIN = "rr"
    RANDOM = "rnd"

    name = StringField(unique=True)
    description = StringField(required=False)
    type = StringField()
    select_policy = StringField(choices=[
        (ALL, "All"),
        (PRIORITY, "Priority"),
        (ROUNDROBIN, "Round-Robin"),
        (RANDOM, "Random")
    ], default=PRIORITY)
    write_concern = IntField(default=1)
    collectors = ListField(EmbeddedDocumentField(CollectorProtocol))
    access = ListField(EmbeddedDocumentField(AccessProtocol))

    def __unicode__(self):
        return self.name

    @property
    def default_collector(self):
        """
        Returns URL of first active
        collector. Returns None if no default collector set
        """
        selectable = [
            c for c in self.collectors
            if c.is_active and c.is_selectable
        ]
        if not selectable:
            return None
        if len(selectable) <= self.write_concern:
            policy = self.ALL
            wc = len(selectable)
        else:
            policy = self.select_policy
            wc = self.write_concern
        return {
            "policy": policy,
            "write_concern": wc,
            "collectors": [
                {
                    "proto": c.protocol,
                    "address": c.address,
                    "port": c.port
                }
                for c in selectable
            ]
        }
