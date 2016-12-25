# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PhoneRange model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
import cachetools

id_lock = Lock()


class PhoneNumberProfile(Document):
    meta = {
        "collection": "noc.phonenumberprofiles"
    }

    name = StringField(unique=True)
    description = StringField()

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PhoneNumberProfile.objects.filter(id=id).first()
