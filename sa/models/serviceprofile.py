# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField
## NOC modules


class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles"
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    label_template = StringField()
    # FontAwesome glyph
    glyph = StringField()

    def __unicode__(self):
        return self.name
