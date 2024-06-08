# ----------------------------------------------------------------------
# IfDescPatterns
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, Dict, Union
from threading import Lock
import operator
import re

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError
import bson
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check


id_lock = Lock()
re_lock = Lock()


class IfDescPatternRule(EmbeddedDocument):
    is_active = BooleanField(default=True)
    pattern = StringField()

    def __str__(self):
        return self.pattern


@on_delete_check(
    check=[
        ("sa.ManagedObjectProfile", "ifdesc_patterns"),
        ("inv.InterfaceProfile", "ifdesc_patterns"),
    ]
)
class IfDescPatterns(Document):
    meta = {
        "collection": "ifdescpatterns",
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField(unique=True)
    description = StringField()
    resolve_remote_port_by_object = BooleanField(default=False)
    patterns = ListField(EmbeddedDocumentField(IfDescPatternRule))

    _id_cache = cachetools.TTLCache(100, ttl=60)
    _re_cache = {}

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[bson.ObjectId, str]) -> Optional["IfDescPatterns"]:
        return IfDescPatterns.objects.filter(id=oid).first()

    def clean(self):
        super().clean()
        for p in self.patterns:
            rx = self._get_re(p.pattern)
            if not rx:
                raise ValidationError("Invalid regular expression: %s" % p.pattern)

    def iter_match(self, s: str) -> Iterable[Dict[str, str]]:
        """
        Match patterns against string yield all matching groups

        :param s: Input string
        :return:
        """
        for rule in self.patterns:
            if not rule.is_active:
                continue
            rx = self._get_re(rule.pattern)
            if not rx:
                continue
            match = rx.search(s)
            if match:
                yield match.groupdict()

    @cachetools.cachedmethod(operator.attrgetter("_re_cache"), lock=lambda _: re_lock)
    def _get_re(self, pattern: str) -> Optional[re.Pattern]:
        try:
            return re.compile(pattern)
        except re.error:
            return None
