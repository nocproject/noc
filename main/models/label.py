# ----------------------------------------------------------------------
# Label model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Set
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField, ReferenceField
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem


id_lock = Lock()


class Label(Document):
    meta = {
        "collection": "labels",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(unique=True)
    description = StringField()
    bg_color1 = IntField(default=0x000000)
    fg_color1 = IntField(default=0xFFFFFF)
    bg_color2 = IntField(default=0x000000)
    fg_color2 = IntField(default=0xFFFFFF)
    # Label scope
    enable_agent = BooleanField()
    enable_service = BooleanField()
    # Exposition scope
    expose_metric = BooleanField()
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Caches
    _name_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Label"]:
        return Label.objects.filter(name=name).first()

    @classmethod
    def merge_labels(cls, *args: List[str]) -> List[str]:
        """
        Merge sets of labels, processing the scopes.

        :param args:
        :return:
        """
        seen_scopes: Set[str] = set()
        seen: Set[str] = set()
        r: List[str] = []
        for labels in args:
            for label in labels:
                if label in seen:
                    continue
                elif "::" in label:
                    scope = label.rsplit("::", 1)[0]
                    if scope in seen_scopes:
                        continue
                    seen_scopes.add(scope)
                r.append(label)
                seen.add(label)
        return r
