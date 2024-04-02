# ---------------------------------------------------------------------
# ObjectDiscovery Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import re
from functools import partial
from typing import List, Dict, Optional, Tuple, Set, Any, Union
from threading import Lock

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
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
from noc.core.model.decorator import on_delete_check
from noc.core.purgatorium import SOURCES, ProtocolCheckResult
from noc.core.prettyjson import to_json
from noc.main.models.pool import Pool
from noc.wf.models.workflow import Workflow

id_lock = Lock()
rules_lock = Lock()


class NetworkRange(EmbeddedDocument):
    network = StringField(required=True)  # Range or prefix
    pool = PlainReferenceField(Pool, required=True)
    exclude = BooleanField(default=False)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"network": self.network}


class CheckItem(EmbeddedDocument):
    check = StringField(required=True)
    port = IntField(default=0)
    arg0 = StringField()  # available, access, condition
    match_state = StringField(choices=["ok", "fail", "any"], default="any")
    match = StringField(choices=["regex", "contains", "eq", "gte", "lte"], default="eq")
    value = StringField()

    def __str__(self):
        if self.arg0:
            return f"{self.check}:{self.port} -> {self.arg0}"
        return f"{self.check}:{self.port}"

    def is_match(self, status: bool, data: Dict[str, Any]) -> bool:
        if not self.value and self.match_state == "any":
            return True
        elif not self.value:
            return status
        key = self.arg0 or self.check
        if key not in data:
            return False
        value = data[key]
        if self.match == "regex":
            return bool(re.match(self.value, value))
        elif self.match == "contains":
            return value in self.value
        elif self.match == "gte":
            return int(value) >= int(self.value)
        return value == self.value

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"check": self.check}
        if self.port:
            r["port"] = self.port
        if self.arg0:
            r["arg0"] = self.arg0
        if self.match and self.value:
            r["match"] = self.match
            r["value"] = self.value
        return r


class SourceItem(EmbeddedDocument):
    source = StringField(choices=list(SOURCES), required=True)
    # Remote system ?
    is_required = BooleanField(default=False)  # Check if source required for match

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"source": self.source, "is_required": self.is_required}


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
    sources: List[SourceItem] = EmbeddedDocumentListField(SourceItem)  # Source match and priority
    update_interval = IntField(default=0)
    expired_ttl = IntField(default=0)  # Time for expired source
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
    action = StringField(
        choices=[
            ("new", "As New"),  # Set Rule, Save Record as New
            ("approve", "Approve"),  # Set Rule, Approve Record
            ("ignore", "Ignore"),  # Set Rule and Send Ignored Signal
            ("skip", "Skip"),  # SkipRule, if Rule Needed for Discovery Settings
        ],
        default="new",
    )
    # label =
    # groups =
    stop_processed = BooleanField(default=False)
    allow_sync = BooleanField(default=True)  # sync record on
    # templates

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _prefix_cache = cachetools.TTLCache(maxsize=10, ttl=600)
    _rules_cache = cachetools.TTLCache(10, ttl=180)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ObjectDiscoveryRule"]:
        return ObjectDiscoveryRule.objects.filter(id=oid).first()

    @classmethod
    def get_rule(
        cls, address, pool: Pool, checks: List["ProtocolCheckResult"]
    ) -> Optional["ObjectDiscoveryRule"]:
        for rule in ObjectDiscoveryRule.objects.filter(is_active=True, action__ne="skip").order_by(
            "preference"
        ):
            if rule.is_match(address, pool, checks):
                return rule
        return

    def on_save(self):
        from noc.sa.models.discoveredobject import DiscoveredObject

        # Set record on rule is_dirty
        DiscoveredObject.objects.filter(rule=self.id).update(is_dirty=True)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            #
            "preference": self.preference,
            "workflow__name": self.workflow.name,
            #
            "network_ranges": [c.json_data for c in self.network_ranges],
            "check_policy": self.check_policy,
            "checks": [c.json_data for c in self.checks],
            #
            "sources": [c.json_data for c in self.sources],
            "action": self.action,
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
            ],
        )

    def is_match(
        self,
        address: str,
        pool: Pool,
        checks: List["ProtocolCheckResult"],
    ) -> bool:
        """
        Check discovered record for match rule
        :param address: IP Address
        :param pool: Discovered pool
        :param checks: List Result of Protocol Checks
        :return:
        """
        address = IP.prefix(address)
        if self.network_ranges:
            r = any([p for p in self.get_prefixes(pool) if address in p])
        else:
            r = True
        if not self.checks:
            return r
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
                pc = check_r[(c.check, c.port or 0)]
                r = c.is_match(pc.status, pc.data)
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

    def get_pool(self, address: str) -> Optional[Pool]:
        """
        Return pool for address
        :param address:
        :return:
        """
        address = IP.prefix(address)
        for net in self.network_ranges:
            prefix = IP.prefix(net.network)
            if address in prefix:
                return net.pool
        return None
