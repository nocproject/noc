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
@on_delete_check(
    check=[
        ("vc.L2Domain", "pool.vlan_filter"),
        ("vc.L2Domain", "vlan_discovery_filter"),
        ("vc.L2DomainProfile", "pool.vlan_filter"),
        ("vc.L2DomainProfile", "vlan_discovery_filter"),
        ("sa.ManagedObjectProfile", "mac_collect_vlanfilter"),
    ]
)
@on_save
class VLANFilter(Document):
    meta = {
        "collection": "vlanfilters",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["include_vlans", "exclude_vlans"],
    }

    name = StringField(unique=True)
    description = StringField()
    include_expression = StringField()
    exclude_expression = StringField()
    include_vlans = ListField(IntField(min_value=1, max_value=4095))
    exclude_vlans = ListField(IntField(min_value=1, max_value=4095))

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
        VLANFilter.compile(self.include_expression)
        self.include_vlans = ranges_to_list(self.include_expression)
        if self.exclude_expression:
            VLANFilter.compile(self.exclude_expression)
            self.exclude_vlans = ranges_to_list(self.exclude_expression)
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
