# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Street object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DictField, BooleanField, DateTimeField)
from noc.lib.nosql import PlainReferenceField
# NOC modules
=======
##----------------------------------------------------------------------
## Street object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DictField, BooleanField, DateTimeField)
from noc.lib.nosql import PlainReferenceField
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from division import Division


class Street(Document):
    meta = {
        "collection": "noc.streets",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["parent", "data"]
    }
    #
    parent = PlainReferenceField(Division)
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Additional data
    # Depends on importer
    data = DictField()
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    def __unicode__(self):
        if self.short_name:
            return "%s, %s" % (self.name, self.short_name)
        else:
            return self.name

    @property
    def full_path(self):
        if not self.parent:
            return ""
        r = [self.parent.full_path, unicode(self)]
        return " | ".join(r)
