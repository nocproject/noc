# ----------------------------------------------------------------------
# L2 Filter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import logging
import re
from typing import Optional

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    ListField,
    IntField,
)
import cachetools

# NOC modules
from noc.main.models.label import Label
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.text import ranges_to_list

rx_l2_filter = re.compile(r"^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$")
id_lock = Lock()
logger = logging.getLogger(__name__)


@Label.match_labels(category="l2filter")
@on_delete_check(check=[("vc.L2Domain", "pool.vlan_filter"), ("vc.L2DomainProfile", "pool.vlan_filter")])
@on_save
class VLANFilter(Document):
    meta = {
        "collection": "l2filters",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "expression_calc",
        ],
    }

    name = StringField(unique=True)
    description = StringField()
    # include_rules = ?include_expression (on web)
    # exclude_rules = ?exclude_expression (on web)
    expression = StringField()
    expression_calc = ListField(IntField(min_value=0, max_value=4096))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _match_cache = cachetools.TTLCache(maxsize=50, ttl=30)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["VLANFilter"]:
        return VLANFilter.objects.filter(id=id).first()

    def save(self, *args, **kwargs):
        """
        Check expression before save
        """
        VLANFilter.compile(self.expression)
        self.expression_calc = ranges_to_list(self.expression)
        super().save(*args, **kwargs)

    @classmethod
    def compile(cls, expression):
        """
        Compile VC Filter expression
        """
        if not rx_l2_filter.match(expression):
            raise SyntaxError
        r = []
        for x in expression.split(","):
            x = x.strip()
            if "-" in x:
                f, t = [int(c.strip()) for c in x.split("-")]
            else:
                f = int(x)
                t = f
            if t < f:
                raise SyntaxError
            r += [(f, t)]
        return r
