# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Geodata
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, PointField
## NOC modules
from layer import Layer
from noc.inv.models.object import Object


class GeoData(Document):
    meta = {
        "collection": "noc.geodata"
    }

    # Layer id
    layer = ReferenceField(Layer)
    # Inventory Object's ObjectId
    object = ReferenceField(Object)
    #
    label = StringField()
    # Spatial data
    data = PointField(auto_index=True)

    def __unicode__(self):
        return self.label or self.object
