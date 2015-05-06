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
    name = StringField()

    def __unicode__(self):
        return "%s: %s" % (unicode(self.object), self.name)


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
    type = StringField(required=False)

    def __unicode__(self):
        return u"<%s>" % ", ".join(unicode(c) for c in self.connection)

    def p2p_get_other(self, object):
        """
        Return other side
        as object, name
        """
        for c in self.connection:
            if c.object != object:
                return c.object, c.name
        return None, None