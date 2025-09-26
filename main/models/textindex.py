# ---------------------------------------------------------------------
# Full-text search index
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import datetime
import re

# Third-party modules
from django.db.models import signals as django_signals
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, DateTimeField

# NOC modules
from noc.models import get_object, get_model_id

logger = logging.getLogger(__name__)


class TextIndex(Document):
    meta = {
        "collection": "noc.textindex",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("model", "object"),
            {
                "fields": ["$title", "$content", "$tags"],
                "default_language": "english",
                "language_override": "language",
                "weights": {"title": 10, "tags": 5, "content": 1},
            },
        ],
    }

    # model name, like 'sa.ManagedObject'
    model = StringField()
    # Object id, converted to string
    object = StringField()
    # Short title
    title = StringField()
    # Content to search
    content = StringField()
    # Card to show in search result
    card = StringField()
    # List of tags
    tags = ListField(StringField())
    # Date of last changed
    changed = DateTimeField()
    language = StringField(default="english")

    rx_phrases = re.compile(r"(\d+(?:[-_.:]\d+)+)")

    def __str__(self):
        return "%s:%s" % (self.model, self.object)

    def get_object(self):
        """
        Return object instance
        :returns: Object instance or None
        """
        return get_object(self.model, self.object)

    @classmethod
    def on_update_model(cls, sender, instance, **kwargs):
        cls.update_index(sender, instance)

    @classmethod
    def on_delete_model(cls, sender, instance, **kwargs):
        cls.delete_index(sender, instance)

    @classmethod
    def update_index(cls, sender, instance):
        data = instance.get_index()
        if not data:
            return
        model_id = get_model_id(sender)
        object_id = str(instance.id)
        logger.info("Update FTS index for %s:%s", model_id, object_id)
        TextIndex._get_collection().update_one(
            {"model": model_id, "object": object_id},
            {
                "$set": {
                    "title": data.get("title"),
                    "content": data.get("content"),
                    "card": data.get("card"),
                    "tags": data.get("labels"),
                    "language": "english",
                    "changed": datetime.datetime.now(),
                }
            },
            upsert=True,
        )

    @classmethod
    def delete_index(cls, sender, instance):
        model_id = get_model_id(sender)
        object_id = str(instance.id)
        logger.info("Remove FTS index for %s:%s", model_id, object_id)
        TextIndex._get_collection().delete_one({"model": model_id, "object": object_id})

    @classmethod
    def search(cls, query, limit=1000):
        # Convert IP, prefixes and MAC addresses to phrases search
        query = cls.rx_phrases.sub('"\\1"', query)
        r = TextIndex._get_collection().aggregate(
            [
                {"$match": {"$text": {"$search": query}}},
                {"$sort": {"score": {"$meta": "textScore"}}},
                {"$limit": limit},
                {
                    "$project": {
                        "_id": 1,
                        "model": 1,
                        "object": 1,
                        "title": 1,
                        "card": 1,
                        "tags": 1,
                        "score": {"$meta": "textScore"},
                    }
                },
            ]
        )
        return list(r)


def full_text_search(cls):
    """
    Decorator to denote models supporting full text search

    @full_text_search
    class MyModel(Model):
        ...
        def get_index(self):
            return {
                "id": ...,
                "title": ....,
                "content": ....,
                "card": ....,
                "tags": ...
            }

        @classmethod
        def get_search_result_url(cls, obj_id):
           return "/api/card/view/mycard/%s/" % obj_id
    """
    assert hasattr(cls, "get_index")
    assert hasattr(cls, "get_search_result_url")
    logger.debug("Adding FTS index for %s", cls._meta)
    if isinstance(cls._meta, dict):
        pass
    else:
        django_signals.post_save.connect(TextIndex.on_update_model, sender=cls)
        django_signals.post_delete.connect(TextIndex.on_delete_model, sender=cls)
    return cls
