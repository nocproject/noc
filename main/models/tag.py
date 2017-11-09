# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Favorites model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.contrib.contenttypes.models import ContentType
# NOC modules
from noc.lib.nosql import Document, IntField, StringField, ListField
from noc.lib.db import QTags


class Tag(Document):
    meta = {
        "collection": "noc.tags",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["models"]
    }

    tag = StringField(unique=True)
    models = ListField(StringField())
    count = IntField(default=0)

    def __unicode__(self):
        return self.tag

    @classmethod
    def register_tag(cls, tag, model):
        """
        Register new tag occurence
        :param tag: Tag Name
        :param model: Model for creating tag
        :return:
        """
        cls._get_collection().update(
            {"tag": tag},
            {
                "$addToSet": {
                    "models": model
                },
                "$inc": {
                    "count": 1
                }
            },
            upsert=True
        )

    @classmethod
    def unregister_tag(cls, tag, model):
        """
        Unregister tag occurence
        :param tag: Tag Name
        :param model: Model for creating tag
        :return:
        """
        r = cls._get_collection().update(
            {"tag": tag},
            {
                "$addToSet": {
                    "models": model
                },
                "$inc": {
                    "count": -1
                }
            },
            upsert=True
        )
        # @todo Remove Tag if count <= 0

    def get_objects(self):
        """
        Return all tagged objects
        :return:
        """
        r = []
        for m in self.models:
            al, mn = m.split("_", 1)
            mc = ContentType.objects.get(app_label=al, model=mn)
            r += [mc.objects.filter(QTags([self.tag]))]
        return r
