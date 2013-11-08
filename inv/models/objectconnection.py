## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectConnection model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DictField,
                                ListField, EmbeddedDocumentField)
## NOC modules
from noc.inv.models.object import Object
from noc.lib.nosql import PlainReferenceField


class ObjectConnectionItem(EmbeddedDocument):
    _meta = {
        "allow_inheritance": False
    }
    # Object reference
    object = PlainReferenceField(Object)
    # Connection name
    connection = StringField()

    def __unicode__(self):
        return "%s: %s" % (object.name, connection)


class ObjectConnection(Document):
    """
    Inventory object connections
    """
    meta = {
        "collection": "noc.objectconnections",
        "allow_inheritance": False,
        "indexes": ["connection"]
    }

    # 2 or more items
    connection = ListField(EmbeddedDocumentField(ObjectConnectionItem))
    data = DictField()

    def __unicode__(self):
        return "<%s>" % ", ".join(unicode(c) for c in self.connection)
