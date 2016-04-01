# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField
import cachetools


class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles"
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    card_title_template = StringField()
    # FontAwesome glyph
    glyph = StringField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @cachetools.cachedmethod(operator.attrgetter("_id_cache"))
    def get_by_id(self, id):
        return ServiceProfile.objects.filter(id=id).first()
