# ---------------------------------------------------------------------
# IgnorePattern model
# Propagated to collectors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, EnumField

# NOC modules
from noc.config import config
from noc.core.change.decorator import change
from noc.core.fm.enum import EventSource

DATASTREAM_RULE_PREFIX = "ignore_pattern"


@change
class IgnorePattern(Document):
    meta = {
        "collection": "noc.fm.ignorepatterns",
        "strict": False,
        "auto_create_index": False,
        "indexes": [{"fields": ("source", "pattern"), "unique": True}],
    }

    source = EnumField(EventSource, default=EventSource.SYSLOG)
    pattern = StringField(required=True)
    is_active = BooleanField(default=True)
    description = StringField(required=False)

    def __str__(self):
        return f"{self.source}: {self.pattern}"

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["IgnorePattern"]:
        return IgnorePattern.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgeventrules:
            yield "cfgeventrules", f"ignore_pattern:{self.id}"

    @classmethod
    def get_rule_config(cls, pattern: "IgnorePattern"):
        """Return MetricConfig for Metrics service"""
        if not pattern.is_active:
            raise KeyError("Rule not activated")
        return {
            "id": f"{DATASTREAM_RULE_PREFIX}:{pattern.id}",
            "$type": DATASTREAM_RULE_PREFIX,
            "name": str(pattern),
            "message_rx": pattern.pattern,
            "sources": [pattern.source],
        }
