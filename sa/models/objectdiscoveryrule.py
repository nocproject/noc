# ---------------------------------------------------------------------
# ObjectDiscovery Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from functools import partial
from typing import List, Dict, Optional, Tuple, Set
from threading import Lock

# Third-party modules
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    ListField,
    StringField,
    BooleanField,
    EmbeddedDocumentListField,
    IntField,
    UUIDField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.core.ip import IPv4, IP
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from noc.core.purgatorium import SOURCES, ProtocolCheckResult
from noc.main.models.pool import Pool

id_lock = Lock()
rules_lock = Lock()


class NetworkRange(EmbeddedDocument):
    network = StringField(required=True)  # Range or prefix
    pool = PlainReferenceField(Pool, required=True)
    exclude = BooleanField(default=False)


class CheckItem(EmbeddedDocument):
    check = StringField(required=True)
    port = IntField(default=0)
    arg0 = StringField()  # available, access, condition
    condition = StringField(choices=["regex", "contains", "eq", "gte", "lte"], default="eq")
    value = StringField()

    def is_match(self, data: ProtocolCheckResult) -> bool:
        if not data.status:
            return False
        if self.value:
            return False
        return True


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
    # Global ID
    uuid = UUIDField(binary=True)
    # Rule preference, processed from lesser to greater
    preference = IntField(required=True, default=100)
    #
    network_ranges: List["NetworkRange"] = EmbeddedDocumentListField(NetworkRange)
    workflow: "Workflow" = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "sa.DiscoveredObject")
    )
    sources: List[str] = ListField(StringField(choices=list(SOURCES)))  # Source match and priority
    update_interval = IntField(default=0)
    expired_ttl = IntField(default=0)  # Time for expired event
    #
    check_policy = StringField(choices=["ALL", "ANY"], default="ALL")
    checks: List["CheckItem"] = EmbeddedDocumentListField(CheckItem)
    #
    # actions: List["MetricActionItem"] = EmbeddedDocumentListField(MetricActionItem)
    # log - add record as new
    # approve - send approve
    # ignore - ignore state
    # UnApprove, manual approve ?
    # duplicate state
    # notification_group
    # notification_template =
    event = StringField(
        choices=[
            ("new", "New"),
            ("approve", "Approve"),
            ("ignore", "Ignore"),
            ("skip", "Skip"),
        ],
        default="new",
    )
    # label =
    # groups =
    stop_processed = BooleanField(default=False)
    # allow_sync = BooleanField(default=True)  # sync record on
    # templates

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _prefix_cache = cachetools.TTLCache(maxsize=10, ttl=600)
    _rules_cache = cachetools.TTLCache(10, ttl=180)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid) -> Optional["ObjectDiscoveryRule"]:
        return ObjectDiscoveryRule.objects.filter(id=oid).first()

    @classmethod
    def get_rule(
        cls, address, pool: Pool, checks: List["ProtocolCheckResult"]
    ) -> Optional["ObjectDiscoveryRule"]:
        for rule in ObjectDiscoveryRule.objects.filter(is_active=True).order_by("preference"):
            if rule.is_match(address, pool, checks):
                return rule
        return

    def is_match(self, address: str, pool: Pool, checks: List["ProtocolCheckResult"]) -> bool:
        """
        Check discovered record for match rule
        :param address: IP Address
        :param pool: Discovered pool
        :param checks: List Result of Protocol Checks
        :return:
        """
        address = IP.prefix(address)
        r = any([p for p in self.get_prefixes(pool) if address in p])
        if not self.network_ranges:
            r = True
        elif not r:
            return False
        all_checks: Set[str] = set()
        check_r: Dict[Tuple[str, int], ProtocolCheckResult] = {}
        for c in checks:
            if c.status:
                all_checks.add(c.check)
                check_r[(c.check, c.port)] = c
                check_r[(c.check, 0)] = c
        for c in self.checks:
            r = False
            if (c.check, c.port or 0) in check_r:
                r = c.is_match(check_r[(c.check, c.port or 0)])
            if not r and self.check_policy == "ALL":
                return False
            if r and self.check_policy == "ANY":
                return True
        return r

    @cachetools.cachedmethod(operator.attrgetter("_prefix_cache"), lock=lambda _: id_lock)
    def get_prefixes(self, pool: Optional[Pool] = None) -> List["IPv4"]:
        """
        Return configured prefixes
        :return:
        """
        r = []
        for net in self.network_ranges:
            if net.exclude or (pool and pool != net.pool):
                continue
            prefix, *range = net.network.split("-")
            if not range:
                r.append(IPv4.prefix(prefix))
            elif len(range) == 1:
                r += IPv4.range_to_prefixes(prefix, range[0])
            else:
                # Unknown format
                continue
        return r
