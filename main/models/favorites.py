<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Favorites model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
# NOC modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Favorites model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import (Document, ForeignKeyField, StringField,
                           BooleanField, ListField)
from noc.main.models import User

logger = logging.getLogger(__name__)


class Favorites(Document):
    meta = {
        "collection": "noc.favorites",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["user", ("user", "app")]
    }

    user = ForeignKeyField(User)
    app = StringField()
    favorite_app = BooleanField(default=False)
    favorites = ListField()

    def unicode(self):
        return "%s:%s" % (self.user.username, self.app)

    @classmethod
    def add_item(cls, user, app_id, item):
        fv = Favorites.objects.filter(
            user=user.id, app=app_id).first()
        if not fv:
            fv = Favorites(user=user.id, app=app_id, favorites=[])
        fi = list(fv.favorites) or []
        if item not in fi:
            logger.info("Setting favorite item %s@%s for user %s",
                        item, app_id, user.username)
            fv.favorites = fi + [item]
            fv.save()

    @classmethod
    def remove_item(cls, user, app_id, item):
        fv = Favorites.objects.filter(
            user=user.id, app=app_id).first()
        fi = list(fv.favorites) or []
        if fv and item and item in fi:
            logger.info("Resetting favorite item %s@%s for user %s",
                        item, app_id, user.username)
            fi.remove(item)
            fv.favorites = fi
<<<<<<< HEAD
            fv.save()
=======
            fv.save()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
