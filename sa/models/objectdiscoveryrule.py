# ---------------------------------------------------------------------
# ObjectDiscovery Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import re
from itertools import filterfalse
from functools import partial
from typing import List, Dict, Optional, Tuple, Set, Any, Union, FrozenSet
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
    ListField,
    ObjectIdField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.change.decorator import change
from noc.core.ip import IPv4, IP
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.purgatorium import SOURCES, ETL_SOURCE
from noc.core.prettyjson import to_json
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.modeltemplate import ModelTemplate
from noc.wf.models.workflow import Workflow

id_lock = Lock()
rules_lock = Lock()


class NetworkRange(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    network = StringField(required=True)  # Range or prefix
    pool = PlainReferenceField(Pool, required=True)
    exclude = BooleanField(default=False)

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"network": self.network}


class CheckItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    check = StringField(required=True)
    port = IntField(default=0)
    arg0 = StringField()

    def __str__(self):
        if self.arg0:
            return f"{self.check}:{self.port} -> {self.arg0}"
        return f"{self.check}:{self.port}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"check": self.check}
        if self.port:
            r["port"] = self.port
        if self.arg0:
            r["arg0"] = self.arg0
        return r


class MatchData(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    field = StringField(required=True)
    op = StringField(choices=["regex", "contains", "==", "!=", "gte", "lte"], default="eq")
    value = StringField(required=True)

    def __str__(self):
        return f"{self.field} {self.op} {self.value}"

    def is_match(self, data):
        if self.field not in data:
            return False
        value = data[self.field]
        if self.op == "regex":
            return bool(re.match(self.value, value))
        elif self.op == "contains":
            return value in self.value
        elif self.op == "gte":
            return int(value) >= int(self.value)
        elif self.op == "lte":
            return int(value) <= int(self.value)
        return value == self.value

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"field": self.field, "op": self.op, "value": self.value}


class MatchCheck(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    check = StringField(required=True)
    port = IntField(required=False)
    match_state = StringField(choices=["ok", "fail", "any"], default="any")

    def __str__(self):
        if self.port:
            return f"{self.check}:{self.port} {self.match_state}"
        return f"{self.check} {self.match_state}"

    def is_match(self, checks: Dict[Tuple[str, int], Optional[bool]]):
        if (self.check, self.port or 0) not in checks:
            return False
        value = checks[(self.check, self.port or 0)]
        if self.match_state == "ok" and not value:
            return False
        elif self.match_state == "fail" and value:
            return False
        return True

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"check": self.check, "match_state": self.match_state}
        if self.port:
            r["port"] = self.port
        return r


class MatchItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    match_labels = ListField(StringField())
    match_groups = ListField(ObjectIdField())
    match_checks = EmbeddedDocumentListField(MatchCheck)
    match_data = EmbeddedDocumentListField(MatchData)
    # Action
    action = StringField(choices=["approve", "skip", "ignore"])

    def __str__(self):
        r = ""
        if self.match_labels:
            r += ",".join(self.match_labels)
        if self.match_checks:
            r += "AND" + ",".join(str(m) for m in self.match_checks)
        if self.match_data:
            r += "AND" + ",".join(str(m) for m in self.match_data)
        return r

    def is_match(
        self,
        labels: List[str],
        data: Dict[str, Any],
        checks: Dict[Tuple[str, int], Any],
        groups: List[str],
    ) -> bool:
        if self.match_labels and set(self.match_labels) - set(labels):
            return False
        if self.match_groups and set(self.match_groups) - set(groups):
            return False
        if self.match_data and not data:
            return False
        elif self.match_data and data:
            return all(d.is_match(data) for d in self.match_data)
        if self.match_checks and not checks:
            return False
        elif self.match_checks and checks:
            return all(c.is_match(checks) for c in self.match_checks)
        return True

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.match_labels:
            r["match_labels"] = self.match_labels
        if self.match_checks:
            r["match_checks"] = [c.json_data for c in self.match_checks]
        if self.match_data:
            r["match_data"] = [c.json_data for c in self.match_data]
        return r


class SourceItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    source = StringField(choices=list(SOURCES), required=True)
    remote_system: Optional[RemoteSystem] = PlainReferenceField(RemoteSystem, required=False)
    update_last_seen = BooleanField(default=False)
    sync_policy = StringField(choices=[("A", "All"), ("M", "Mappings Only")], default="A")
    remove_policy = StringField(
        choices=[("D", "Disable"), ("U", "Unmanaged"), ("R", "Remove")], default="D"
    )
    deny_create = BooleanField(default=False)
    is_required = BooleanField(default=False)  # Check if source required for match

    def __str__(self):
        if self.remote_system:
            return f"{self.source}#{self.remote_system.name}: ULS: {self.update_last_seen};P: {self.sync_policy};R:{self.is_required}"
        return f"{self.source}: ULS: {self.update_last_seen};P: {self.sync_policy};R:{self.is_required}"

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"source": self.source, "is_required": self.is_required}


@change
@on_save
@on_delete_check(check=[("sa.DiscoveredObject", "rule")])
class ObjectDiscoveryRule(Document):
    meta = {
        "collection": "objectdiscoveryrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.objectdiscoveryrules",
        "json_unique_fields": ["name"],
    }
    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=True)
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
    # deduplicate_fields =
    conditions: List[MatchItem] = EmbeddedDocumentListField(MatchItem)
    update_interval = IntField(default=0)
    expired_ttl = IntField(default=0)  # Time for expired source
    #
    enable_ip_scan_discovery = BooleanField(default=False)
    ip_scan_discovery_interval = IntField(default=3600)
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
    default_action = StringField(
        choices=[
            ("new", "As New"),  # Set Rule, Save Record as New
            ("approve", "Approve"),  # Set Rule, Approve Record
            # ("remove", "Remove"),  # Set Rule and Send Ignored Signal
            ("ignore", "Ignore"),  # Ignore Record
            ("skip", "Skip"),  # SkipRule, if Rule Needed for Discovery Settings
            ("log", "Log"),  # Log that rule match
        ],
        default="new",
    )
    # stop_processed = BooleanField(default=False)
    sync_approved = BooleanField(default=False)  # sync record on
    default_template: Optional[ModelTemplate] = PlainReferenceField(ModelTemplate)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _prefix_cache = cachetools.TTLCache(maxsize=10, ttl=600)
    _rules_cache = cachetools.TTLCache(10, ttl=90)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ObjectDiscoveryRule"]:
        return ObjectDiscoveryRule.objects.filter(id=oid).first()

    @property
    def required_sources(self) -> FrozenSet[str]:
        """Return required sources for rule"""
        return frozenset(s.source for s in self.sources if s.is_required)

    @property
    def required_systems(self) -> FrozenSet[str]:
        """Return required RemoteSystems for rule"""
        return frozenset(
            str(s.remote_system.id) for s in self.sources if s.is_required and s.remote_system
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_rules_by_source(cls, sources: Optional[FrozenSet[str]] = None):
        """
        Return list rules match Instance for sources
        Args:
            sources:
        """
        r = []
        for rule in ObjectDiscoveryRule.objects.filter(
            is_active=True, default_action__ne="skip"
        ).order_by("preference"):
            if sources and rule.required_sources and (rule.required_sources - sources):
                continue
            r.append(rule)
        return r

    @classmethod
    def get_effective_data(
        cls, sources: List[str], data: List[Any]
    ) -> Tuple[Dict[str, str], Set[str], Set[str]]:
        """
        Merge data by Source Priority
        Args:
            sources: List sources getting data
            data: Effective data on source
        """
        r = {}
        labels, groups = set(), set()
        for di in sorted(
            filterfalse(lambda d: d.source not in sources, data),
            key=lambda x: sources.index(x.source),
        ):
            for key, value in di.data.items():
                if key in r or not value:
                    continue
                r[key] = value
            if di.labels:
                labels |= set(di.labels)
            if di.service_groups:
                groups |= set(di.service_groups)
        return r, labels, groups

    def merge_sources(self, sources: List[str]) -> List[str]:
        """Merge based source and Rules source ->"""
        if not self.sources:
            return sources
        rs = [s.source for s in self.sources]
        return sorted(
            set(rs).intersection(set(sources)), key=lambda x: rs.index(x) if x in rs else 999
        )

    @classmethod
    def get_rule(
        cls,
        address,
        pool: Pool,
        checks: List[Any],
        data: Optional[List[Any]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional["ObjectDiscoveryRule"]:
        """
        Return Effective rule by discovered data

        Args:
            address: IP Address for record
            pool: IP Address Pool
            checks: Check Result Status
            data: Effective data dict: DataItem
            sources: List sources for record

        """
        ss = frozenset(sources)
        for rule in ObjectDiscoveryRule.get_rules_by_source(ss):
            if ETL_SOURCE in ss and rule.required_systems - {
                str(d.remote_system.id) for d in data if d.remote_system
            }:
                continue
            r_data, r_labels, r_groups = cls.get_effective_data(
                [s.source for s in rule.sources] or sources, data
            )
            if rule.is_match(address, pool, checks, r_labels, r_data, r_groups):
                return rule

    def on_save(self):
        """
        Refresh records after update rule
        """
        from noc.sa.models.discoveredobject import DiscoveredObject

        changed_fields = frozenset(getattr(self, "_changed_fields", None) or [])
        if not changed_fields or changed_fields.intersection(
            ["sources", "default_action", "sync_approved"]
        ):
            # Set record on rule is_dirty
            DiscoveredObject.objects.filter(rule=self.id).update(is_dirty=True)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "is_active": self.is_active,
            "description": self.description,
            #
            "preference": self.preference,
            "workflow__uuid": str(self.workflow.uuid),
            #
            "network_ranges": [c.json_data for c in self.network_ranges],
            "checks": [c.json_data for c in self.checks],
            #
            "sources": [c.json_data for c in self.sources],
            "conditions": [c.json_data for c in self.conditions],
            "enable_ip_scan_discovery": self.enable_ip_scan_discovery,
            "ip_scan_discovery_interval": self.ip_scan_discovery_interval,
            "default_action": self.default_action,
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

    @staticmethod
    def parse_check(checks: List[Any]) -> Dict[Tuple[str, int], bool]:
        """
        Parse Check Result list to Dict

        Args:
            checks: - List of Check Result

        """
        all_checks: Set[str] = set()
        check_r: Dict[Tuple[str, int], bool] = {}
        for c in checks:
            if not c.skipped:
                all_checks.add(c.name)
                check_r[(c.name, c.port)] = c.status
                check_r[(c.name, 0)] = c.status
        return check_r

    def is_match(
        self,
        address: str,
        pool: Pool,
        checks: List[Any],
        labels: List[str],
        data: Dict[str, Any],
        groups: List[str],
    ) -> bool:
        """
        Check discovered record for match rule

        Args:
            address: IP Address
            pool: Discovered pool
            checks: List Result of Protocol Checks
            labels: Labels list
            data: Effective data
            groups: record groups
        """
        address = IP.prefix(address)
        if self.network_ranges:
            if not any([p for p in self.get_prefixes(pool) if address in p]):
                return False
        if not self.conditions:
            return True
        checks = self.parse_check(checks)
        return any(c.is_match(labels, data, checks, groups) for c in self.conditions)

    @cachetools.cachedmethod(operator.attrgetter("_prefix_cache"), lock=lambda _: id_lock)
    def get_prefixes(self, pool: Optional[Pool] = None) -> List["IPv4"]:
        """Return configured prefixes"""
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
        Args:
            address: IP Address for check
        """
        address = IP.prefix(address)
        for net in self.network_ranges:
            prefix = IP.prefix(net.network)
            if address in prefix:
                return net.pool
        return None

    def get_action(
        self,
        checks: List[Any],
        labels: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        groups: Optional[List[str]] = None,
    ) -> str:
        """
        Return Discovered object action
        Args:
            checks: Discovered object checks result
            labels: Labels list
            data: Collected effective data
            groups: Groups
        """
        checks = self.parse_check(checks)
        action = None
        for c in self.conditions:
            if c.is_match(labels, data, checks, groups or set()) and c.action:
                action = c.action
        return action or self.default_action

    def get_sync_settings(
        self,
        source,
        remote_system: Optional[RemoteSystem] = None,
    ) -> Optional[SourceItem]:
        """Get synced Setting for source"""
        r = None
        for s in self.sources:
            if s.source != source:
                continue
            elif not remote_system and source != "etl":
                r = s
                break
            elif s.remote_system == remote_system:
                r = s
                break
            elif not s.remote_system:
                r = s
        return r
