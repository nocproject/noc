# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Subscriber Profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField
# NOC models
from noc.lib.nosql import ForeignKeyField
from noc.main.models.style import Style


class SubscriberProfile(Document):
    meta = {
        "collection": "noc.subscriberprofiles"
    }

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    tags = ListField(StringField())

    def __unicode__(self):
        return self.name
