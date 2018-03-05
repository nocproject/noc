# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Dashboard storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, ListField,
                                IntField, BinaryField, EmbeddedDocumentField)
# NOC modules
from noc.main.models import User, Group
from noc.lib.nosql import ForeignKeyField

DAL_NONE = -1
DAL_RO = 0
DAL_MODIFY = 1
DAL_ADMIN = 2


class DashboardAccess(EmbeddedDocument):
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    level = IntField(choices=[
        (DAL_RO, "Read-only"),
        (DAL_MODIFY, "Modify"),
        (DAL_ADMIN, "Admin")
    ])


class Dashboard(Document):
    meta = {
        "collection": "noc.dashboards",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "owner", "tags"
        ]
    }

    title = StringField()
    # Username
    owner = ForeignKeyField(User)
    #
    description = StringField()
    #
    tags = ListField(StringField())
    # Config format version
    format = IntField(default=1)
    # gzip'ed data
    config = BinaryField()
    #
    created = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)
    #
    access = ListField(EmbeddedDocumentField(DashboardAccess))

    def __unicode__(self):
        return self.title

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

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, **kwargs):
        # Split DashBoard Acces to {User, level}, {Group, level}
        # self.update(add_to_set__access=[parent_1, parent_2, parent_1])
        if "access" in getattr(self, '_changed_fields', []):
            # Check unique
            processed = []
            access = []
            for da in sorted(self.access, reverse=True):
                # Deduplicate rights
                # @todo changing priority (reverse order)
                if da.user and "u%d" % da.user.id in processed:
                    continue
                elif da.group and "g%d" % da.group.id in processed:
                    continue
                if da.user and da.group:
                    # Split User and Group rights
                    access += [DashboardAccess(user=da.user.id, level=da.level),
                               DashboardAccess(group=da.group.id, level=da.level)]
                    processed += ["u%d" % da.user.id, "g%d" % da.group.id]
                    continue
                access += [da]
                if da.user:
                    processed += ["u%d" % da.user.id]
                if da.group:
                    processed += ["g%d" % da.group.id]
            self.access = access

        super(Dashboard, self).save(
            force_insert=force_insert, validate=validate, clean=clean,
            write_concern=write_concern, cascade=cascade,
            cascade_kwargs=cascade_kwargs, _refs=_refs,
            save_condition=save_condition, **kwargs)

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
        self._get_collection().update(match, update)
