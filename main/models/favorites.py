## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Favorites model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, ForeignKeyField, StringField,
                           BooleanField, ListField)
from noc.main.models import User


class Favorites(Document):
    meta = {
        "collection": "noc.favorites",
        "allow_inheritance": False,
        "indexes": ["user", ("user", "app")]
    }

    user = ForeignKeyField(User)
    app = StringField()
    favorite_app = BooleanField(default=False)
    favorites = ListField()

    def unicode(self):
        return "%s:%s" % (self.user.username, self.app)
