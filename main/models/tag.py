# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Favorites model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import Document, IntField, StringField, ListField


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
        cls._get_collection().update_one(
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
        cls._get_collection().update_one(
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
