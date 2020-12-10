# ---------------------------------------------------------------------
# MIBData model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Tuple, Any

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, ListField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .mib import MIB


class MIBData(Document):
    meta = {
        "collection": "noc.mibdata",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["name", "mib", "aliases"],
    }
    mib = PlainReferenceField(MIB)
    oid = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField(required=False)
    syntax = DictField(required=False)
    aliases = ListField(StringField(), default=[])

    _name_syntax_cache: Dict[str, Tuple[str, Dict[str, Any]]] = {}

    def __str__(self):
        return self.name

    @classmethod
    def preload(cls):
        """
        Preload data and heat up cache
        :return:
        """
        cls._name_syntax_cache = {
            d["oid"]: (d["name"], d["syntax"] or {})
            for d in cls._get_collection().find({}, {"_id": 0, "oid": 1, "name": 1, "syntax": 1})
        }
        cls.get_name_and_syntax = cls._get_name_and_syntax_cached

    @classmethod
    def _get_name_and_syntax_uncached(
        cls, oid: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        d = cls._get_collection().find_one({"oid": oid}, {"_id": 0, "name": 1, "syntax": 1})
        if d:
            return d["name"], d["syntax"] or {}
        return None, None

    @classmethod
    def _get_name_and_syntax_cached(
        cls, oid: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        r = cls._name_syntax_cache.get(oid)
        if r:
            return r
        return None, None

    get_name_and_syntax = _get_name_and_syntax_uncached
