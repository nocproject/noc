# ---------------------------------------------------------------------
# Favorites model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
from typing import Any, Iterable

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, BooleanField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.aaa.models.user import User

logger = logging.getLogger(__name__)


class Favorites(Document):
    meta = {
        "collection": "noc.favorites",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("user", "app")],
    }

    user = ForeignKeyField(User)
    app = StringField()
    favorite_app = BooleanField(default=False)
    favorites = ListField()

    def __str__(self):
        return f"{self.user.username}:{self.app}"

    @classmethod
    def add_item(cls, user: User, app_id: str, item: Any) -> None:
        fv = Favorites.objects.filter(user=user.id, app=app_id).first()
        if not fv:
            fv = Favorites(user=user.id, app=app_id, favorites=[])
        fi = list(fv.favorites) or []
        if item not in fi:
            logger.info("Setting favorite item %s@%s for user %s", item, app_id, user.username)
            fv.favorites = fi + [item]
            fv.save()

    @classmethod
    def add_items(cls, user: User, app_id: str, items: Iterable[Any]) -> None:
        fv = Favorites.objects.filter(user=user.id, app=app_id).first()
        if not fv:
            fv = Favorites(user=user.id, app=app_id, favorites=[])
        fi = list(fv.favorites) or []
        current = set(fi)
        to_add = set(items) - current
        if to_add:
            for item in to_add:
                logger.info("Setting favorite item %s@%s for user %s", item, app_id, user.username)
            fv.favorites = fi + list(to_add)
            fv.save()

    @classmethod
    def remove_item(cls, user: User, app_id: str, item: Any):
        fv = Favorites.objects.filter(user=user.id, app=app_id).first()
        fi = list(fv.favorites) or []
        if fv and item and item in fi:
            logger.info("Resetting favorite item %s@%s for user %s", item, app_id, user.username)
            fi.remove(item)
            fv.favorites = fi
            fv.save()

    @classmethod
    def remove_items(cls, user: User, app_id: str, items: Iterable[Any]):
        fv = Favorites.objects.filter(user=user.id, app=app_id).first()
        if not fv:
            return
        fi = list(fv.favorites) or []
        current = set(fi)
        s_items = set(items)
        to_remove = current.intersection(s_items)
        if to_remove:
            for item in to_remove:
                logger.info(
                    "Resetting favorite item %s@%s for user %s", item, app_id, user.username
                )
            fv.favorites = [item for item in fv.favorites if item not in s_items]
            fv.save()
