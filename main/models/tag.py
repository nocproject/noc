# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Favorites model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, ListField


@six.python_2_unicode_compatible
class Tag(Document):
    meta = {
        "collection": "noc.tags",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["models"],
    }

    tag = StringField(unique=True)
    models = ListField(StringField())
    count = IntField(default=0)

    def __str__(self):
        return self.tag

    @classmethod
    def register_tag(cls, tag, model):
        """
        Register new tag occurence
        :param tag: Tag Name
        :param model: Model for creating tag
        :return:
        """
        cls._get_collection().update_one(
            {"tag": tag}, {"$addToSet": {"models": model}, "$inc": {"count": 1}}, upsert=True
        )

    @classmethod
    def unregister_tag(cls, tag, model):
        """
        Unregister tag occurence
        :param tag: Tag Name
        :param model: Model for creating tag
        :return:
        """
        cls._get_collection().update_one(
            {"tag": tag}, {"$addToSet": {"models": model}, "$inc": {"count": -1}}, upsert=True
        )
        # @todo Remove Tag if count <= 0
