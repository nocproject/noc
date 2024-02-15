# ---------------------------------------------------------------------
# ObjectDiscovery Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from collections import defaultdict
from functools import partial
from typing import List, Dict, Any, Optional, Tuple, Set
from threading import Lock

# Third-party modules
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    FloatField,
    ListField,
    DictField,
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.main.models.label import Label
from noc.config import config

id_lock = Lock()
rules_lock = Lock()


@change
@on_delete_check(check=[("sa.DiscoveredObject", "rule")])
class ObjectDiscoveryRule(Document):
    meta = {
        "collection": "objectdiscoveryrules",
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=False)
    #
    networks = ListField(StringField())
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "sa.ObjectDiscoveryRule")
    )
    # sources
    #
    # match: List["Match"] = EmbeddedDocumentListField(Match)
    #
    # actions: List["MetricActionItem"] = EmbeddedDocumentListField(MetricActionItem)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _rules_cache = cachetools.TTLCache(10, ttl=180)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid) -> Optional["ObjectDiscoveryRule"]:
        return ObjectDiscoveryRule.objects.filter(id=oid).first()

    # def iter_changed_datastream(self, changed_fields=None):
    #     ...
