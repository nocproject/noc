# ----------------------------------------------------------------------
# Dashboard storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from base64 import b85encode
from pathlib import Path

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ListField,
    IntField,
    BinaryField,
    EmbeddedDocumentField,
    UUIDField,
)

# NOC modules
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.core.mongo.fields import ForeignKeyField
from noc.core.prettyjson import to_json
from noc.core.comp import smart_text
from noc.core.path import safe_json_path

DAL_NONE = -1
DAL_RO = 0
DAL_MODIFY = 1
DAL_ADMIN = 2


class DashboardAccess(EmbeddedDocument):
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    level = IntField(choices=[(DAL_RO, "Read-only"), (DAL_MODIFY, "Modify"), (DAL_ADMIN, "Admin")])


class Dashboard(Document):
    meta = {
        "collection": "noc.dashboards",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["owner", "tags"],
        "json_collection": "bi.dashboards",
        "json_unique_fields": ["uuid"],
    }

    title = StringField()
    # Username
    owner = ForeignKeyField(User)
    description = StringField()
    tags = ListField(StringField())
    # Config format version
    format = IntField(default=1)
    # gzip'ed data
    config = BinaryField()
    created = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)
    access = ListField(EmbeddedDocumentField(DashboardAccess))
    # Global ID
    uuid = UUIDField(binary=True, unique=True)

    def __str__(self):
        return self.title or str(self.uuid)

    @property
    def name(self):
        # For collection sync
        return "%s: %s" % (
            self.owner.username if self.owner else "noc",
            self.title or str(self.uuid),
        )

    def get_user_access(self, user):
        # Direct match as owner
        if user == self.owner or user.is_superuser:
            return DAL_ADMIN
        level = DAL_NONE
        groups = user.groups.all()
        for ar in self.access:
            if ar.user and ar.user == user:
                level = max(level, ar.level)
            if ar.group and ar.group in groups:
                level = max(level, ar.level)
            if level == DAL_ADMIN:
                return level
        return level

    def save(
        self,
        force_insert=False,
        validate=True,
        clean=True,
        write_concern=None,
        cascade=None,
        cascade_kwargs=None,
        _refs=None,
        save_condition=None,
        **kwargs,
    ):
        # Split DashBoard Acces to {User, level}, {Group, level}
        # self.update(add_to_set__access=[parent_1, parent_2, parent_1])
        if "access" in getattr(self, "_changed_fields", []):
            # Check unique
            processed = []
            access = []
            for da in sorted(self.access, reverse=True, key=lambda x: x.level):
                # Deduplicate rights
                # @todo changing priority (reverse order)
                if da.user and "u%d" % da.user.id in processed:
                    continue
                if da.group and "g%d" % da.group.id in processed:
                    continue
                if da.user and da.group:
                    # Split User and Group rights
                    access += [
                        DashboardAccess(user=da.user.id, level=da.level),
                        DashboardAccess(group=da.group.id, level=da.level),
                    ]
                    processed += ["u%d" % da.user.id, "g%d" % da.group.id]
                    continue
                access += [da]
                if da.user:
                    processed += ["u%d" % da.user.id]
                if da.group:
                    processed += ["g%d" % da.group.id]
            self.access = access

        super().save(
            force_insert=force_insert,
            validate=validate,
            clean=clean,
            write_concern=write_concern,
            cascade=cascade,
            cascade_kwargs=cascade_kwargs,
            _refs=_refs,
            save_condition=save_condition,
            **kwargs,
        )

    def clean_access(self, item=None):
        """
        Clean access rights
        update2 = {"$push": {"access": {"$each": [{"user": i.user.id, "level": i.level} for i in items]}}}
        :param item: All, user, group
        :return:
        """
        match = {"_id": self.id}
        if item == "user":
            update = {"$pull": {"access": {"user": {"$exists": True}}}}
        elif item == "group":
            update = {"$pull": {"access": {"group": {"$exists": True}}}}
        else:
            update = {"$pull": "access"}
        self._get_collection().update_many(match, update)

    def to_json(self) -> str:
        return to_json(
            {
                "title": self.title,
                "$collection": self._meta["json_collection"],
                "uuid": str(self.uuid),
                "description": self.description,
                "format": self.format,
                "config": smart_text(b85encode(self.config)),
                "created": self.created.isoformat(),
                "changed": self.changed.isoformat(),
            },
            order=["title", "uuid", "description", "created"],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(str(self.uuid))
