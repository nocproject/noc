# ---------------------------------------------------------------------
# Discovered Object model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Optional, List, Any, Union

# Third-party modules
import orjson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    LongField,
    ListField,
    DateTimeField,
    DictField,
    BooleanField,
    ReferenceField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.clickhouse.connect import connection
from noc.core.purgatorium import ProtocolCheckResult, SOURCES, ETL_SOURCE
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.ip import IP, PrefixDB
from noc.main.models.pool import Pool
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule
from noc.sa.models.managedobject import ManagedObject
from noc.pm.models.agent import Agent
from noc.wf.models.state import State

# Data source, data: Dict[str, str], source -> MergeRule[field-> policy]

PURGATORIUM_SQL = """
SELECT
    IPv4NumToString(ip) as address,
    pool,
    groupArray(source) as sources,
    groupArray((source, remote_system, map('hostname', hostname, 'description', description, 'uptime', toString(uptime), 'remote_id', remote_id, 'ts', toString(max_ts)), data, labels)) as all_data,
    groupUniqArrayArray(checks) as all_checks,
    groupUniqArrayArray(labels) as all_labels
FROM (
    SELECT ip, pool, remote_system,
     argMax(source, ts) as source, argMax(hostname, ts) as hostname, argMax(description, ts) as description,
     argMax(uptime, ts) as uptime, argMax(remote_id, ts) as remote_id, argMax(checks, ts) as checks, 
     argMax(data, ts) as data, argMax(labels, ts) as labels, argMax(ts, ts) as max_ts
    FROM noc.purgatorium
    GROUP BY ip, pool, remote_system
    )
GROUP BY ip, pool
ORDER BY ip
FORMAT JSONEachRow
"""

logger = logging.getLogger(__name__)


class CheckData(EmbeddedDocument):
    name = StringField()
    status: bool = BooleanField()  # True - OK, False - Fail
    # skipped: bool = False  # Check was skipped (Example, no credential)
    # arg0: Optional[str] = None
    # error: Optional[str] = None  # Description if Fail
    data: Dict[str, Any] = DictField()  # Collected check data

    def check_condition(self):
        """

        :return:
        """


@dataclass
class PurgatoriumData(object):
    source: str
    remote_system: Optional[str] = None
    labels: Optional[List[str]] = None
    data: Optional[Dict[str, str]] = None


class CheckStatus(EmbeddedDocument):
    name: str = StringField(required=True)
    port: int = IntField(required=False)
    status: bool = BooleanField(default=True)  # True - OK, False - Fail
    arg0: Optional[str] = StringField(required=False)
    skipped: bool = BooleanField(default=False)
    # data: Dict[str, str] # (for rules check)
    error: Optional[str] = StringField(required=False)  # Description if Fail

    def check_condition(self):
        """

        :return:
        """


class DataItem(EmbeddedDocument):
    source: str = StringField(required=True)
    remote_system: "RemoteSystem" = ReferenceField(RemoteSystem, required=False)
    remote_id: str = StringField(required=False)
    labels: List[str] = ListField(StringField())
    data = DictField()

    def __eq__(self, other: "DataItem") -> bool:
        if self.source != other.source:
            return False
        if other.remote_system and other.remote_system != self.remote_system:
            return False
        if self.data != other.data:
            return False
        return True

    def __hash__(self):
        if self.remote_system:
            hash(
                (
                    self.source,
                    str(self.remote_system.id),
                    self.remote_id,
                    frozenset(self.labels),
                    frozenset((k, v) for k, v in self.data.items()),
                )
            )
        return hash(
            (self.source, frozenset(self.labels), frozenset((k, v) for k, v in self.data.items()))
        )


@bi_sync
@workflow
class DiscoveredObject(Document):
    meta = {
        "collection": "discoveredobjects",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["pool", "address"], "unique": True},
            {"fields": ["pool", "address_bin"]},
            "address_bin",
            "sources",
            "is_dirty",
            "state",
            "effective_labels",
            "hostname",
        ],
    }

    pool: "Pool" = PlainReferenceField(Pool, required=True)
    address: str = StringField(required=True)
    address_bin = IntField()
    state: "State" = PlainReferenceField(State)
    # profile = Predefined Profile
    # Flags
    is_dirty = BooleanField(default=True)
    origin = ReferenceField("self", required=False)
    # is_conflicted
    label = StringField()
    description = StringField()
    hostname = StringField()
    chassis_id = StringField()
    # Sources that find object,     timestamp: str = DateTimeField(required=True)
    sources = ListField(StringField(choices=sorted(SOURCES)))
    # Timestamp of last seen
    last_seen = DateTimeField()
    state_changed = DateTimeField()
    # Timestamp expired
    expired = DateTimeField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # checks
    checks: List[CheckStatus] = EmbeddedDocumentListField(CheckStatus)
    data: List[DataItem] = EmbeddedDocumentListField(DataItem)
    #
    managed_object: "ManagedObject" = ForeignKeyField(ManagedObject)
    # Link to agent
    agent: "Agent" = PlainReferenceField(Agent)
    # Link to Rule
    rule: "ObjectDiscoveryRule" = PlainReferenceField(ObjectDiscoveryRule, required=False)
    #
    effective_data: Dict[str, str] = DictField()
    # Labels
    extra_labels: Dict[str, List[str]] = DictField()
    labels: List[str] = ListField(StringField())  # Manual Set
    effective_labels: List[str] = ListField(StringField())
    #
    bi_id = LongField(unique=True)
    # Comments ?

    PROFILE_LINK = "rule"

    def __str__(self):
        return f"{self.address}({self.pool})"

    def clean(self):
        """
        Sync data and labels
        rules - Merge/Update Rules
          * update data, for rules
            * field
            * source_priority
            * policy- set, replace, union (for list)
        :return:
        """
        #
        data, labels, changed = {}, [], False
        for di in sorted(self.data, key=lambda x: self.sources.index(x.source)):
            for key, value in di.data.items():
                if key in data or not value:
                    # Already set by priority source
                    continue
                data[key] = value
                if key not in self.effective_data or self.effective_data[key] != value:
                    changed = True
            if di.labels:
                labels += di.labels
        # Update Extra Labels
        if self.extra_labels:
            labels += [ll for ll in Label.merge_labels(self.extra_labels.values())]
        if not changed or set(self.effective_labels) != set(labels):
            return
        self.address_bin = IP.prefix(self.address).d
        self.is_dirty = True  # if data changed
        self.hostname = data.get("hostname")
        self.description = data.get("description")
        self.chassis_id = data.get("chassis_id")
        self.effective_data = data
        self.effective_labels = labels

    def get_effective_data(self) -> Dict[str, str]:
        """
        Merge data by Source Priority
        :return:
        """
        data, labels = {}, set()
        for di in sorted(self.data, key=lambda x: self.sources.index(x.source)):
            for key, value in di.data.items():
                if key in data or not value:
                    continue
                data[key] = value
            if di.labels:
                labels |= set(di.labels)
        return data

    def change_rule(self, rule):
        self.rule = rule
        self.save()

    @classmethod
    def register(
        cls,
        pool: Union[str, Pool],
        address: str,
        sources: List[str],
        data: List[PurgatoriumData],  # source, remote_system, data
        checks: Optional[List[ProtocolCheckResult]] = None,
        labels: Optional[List[str]] = None,  # Manual Labels
        timestamp: Optional[datetime.datetime] = None,
        rule=None,  # Processed rule
    ) -> Optional["DiscoveredObject"]:  # MergeRule
        """
        Register New record
        1. Ensure Discovery Object
        2. Update Data obj.update_data(
        3. Rules = for merge data
        is_dirty = True
        :param pool: Address Pool ? default
        :param address: Check Address
        :param sources: List available sources ?from data
        :param data: Source, labels, data
        :param checks: List of checks
        :param labels: Manual Set labels
        :param timestamp: Updated timestamp
        :param rule:
        :return:
        """
        if not isinstance(pool, Pool):
            pool = Pool.get_by_name(pool)
        o = DiscoveredObject.objects.filter(pool=pool, address=address).first()
        # timestamp = timestamp or datetime.datetime.now()
        if not o:
            o = DiscoveredObject(
                pool=pool,
                address=address,
                sources=sources,
                labels=labels or [],
                rule=rule,
            )
        o.rule = rule or ObjectDiscoveryRule.get_rule(address, pool, checks)
        if not o.rule:
            logger.warning("[%s|%s] Not find rule for address. Skipping", pool.name, address)
            return
        o.seen(sources)  # Timestamp
        o.update_data(data, checks)
        o.save()
        return o

    def seen(self, sources: List[str], bulk: Optional[List[Any]] = None):
        """
        Seen Discovered Object
        bulk mode
        * if record on purgatorium and not expired
        """
        # Sorted by rule
        if set(self.sources) != set(sources):
            self.sources = list(set(self.sources or []).union(set(sources)))
            if bulk is not None:
                ...
            else:
                self._get_collection().update_one(
                    {"_id": self.id}, {"$addToSet": {"sources": self.sources}}
                )
        self.fire_event("seen")
        self.touch()  # Workflow expired

    def unseen(self, sources: List[str], bulk: Optional[List[Any]] = None):
        """
        Unseen Discovered Object
        bulk mode
        Unseen record:
         * if delete
         * for expired (by rule)
        """
        # Sorted by rule
        sources = set(self.sources) - set(sources)
        if sources != set(self.sources):
            self.sources = list(set(self.sources or []) - set(sources))
            self._get_collection().update_one(
                {"_id": self.id}, {"$pull": {"sources": self.sources}}
            )
        elif not sources:
            # For empty source, clean sources
            self.sources = []
            self._get_collection().update_one({"_id": self.id}, {"$set": {"sources": []}})
        if not self.sources:
            # source - None, set sensor to missed
            self.fire_event("missed")
            self.touch()

    def sync(self):
        """
        Sync with ManagedObject or Agent
        :return:
        """

    def set_data(
        self,
        source,
        data: Dict[str, str],
        labels: Optional[List[str]] = None,
        remote_system: Optional[str] = None,
    ):
        if source == ETL_SOURCE and not remote_system:
            raise AttributeError("remote_system param is required for 'etl' source")
        for d in self.data:
            if d.source != source:
                continue
            if remote_system and remote_system != d.remote_system:
                continue
            d.data = data
            d.labels = labels or []
            break
        else:
            self.data += [
                DataItem(
                    source=source,
                    remote_system=remote_system,
                    remote_id=data.pop("remote_id", None),
                    labels=labels,
                    data=data,
                )
            ]

    def update_data(
        self,
        data: Optional[List[PurgatoriumData]] = None,
        checks: Optional[List[ProtocolCheckResult]] = None,
    ):
        """
        *
        # source, remote_system, data, labels, checks
        bulk ?
        :param data:
        :param checks:
        :return:
        """
        # Merge Data
        for d in data:
            if d.source not in self.sources:
                # Skip data if not in source
                continue
            rs = None
            if d.remote_system:
                rs = RemoteSystem.get_by_name(d.remote_system)
            self.set_data(d.source, d.data, d.labels, remote_system=rs)
        if checks:
            self.checks = [
                CheckStatus(name=c.check, status=c.status, port=c.port, error=c.error)
                for c in checks
            ]


def sync_purgatorium():
    """
    Sync Discovered object with Purgatorium
    1. Load CHUNK from Purgatorium
    2. Query records from DiscoveredObject
    3. -> register (for new), seen/unseen, update_data (update_data, is_dirty)
     new - Not in DiscoveredObject

    approve/sync:
        query is_dirty records
        check iter_over rules, store rule in records, change workflow? migrate workflow...
        approve/sync

     approve ?
    :return:
    """
    logger.info("Start Purgatorium Sync")
    db = PrefixDB()
    ranges = defaultdict(list)
    for r in ObjectDiscoveryRule.objects.filter(is_active=True):
        for p in r.get_prefixes():
            ranges[p].append(r)
    for prefix, rules in ranges.items():
        db[prefix] = rules
    ch = connection()
    r = ch.execute(PURGATORIUM_SQL, return_raw=True)
    for row in r.splitlines():
        row = orjson.loads(row)
        pool = Pool.get_by_bi_id(row["pool"])
        data = defaultdict(dict)
        # hostnames, descriptions, uptimes, all_data,
        for source, rs, d1, d2, labels in row["all_data"]:
            if d1["uptime"] == "0":
                del d1["uptime"]
            if not rs:
                del d1["remote_id"]
            if rs:
                rs = RemoteSystem.objects.filter(bi_id=rs).first()
                if not rs:
                    continue
                rs = rs.name
            # Check timestamp
            data[(source, rs)].update(d1 | d2)
        rule = None
        DiscoveredObject.register(
            pool,
            row["address"],
            list(set(row["sources"])),
            data=[
                PurgatoriumData(
                    source=source,
                    remote_system=rs,
                    data=d,
                )
                for (source, rs), d in data.items()
            ],
            checks=[ProtocolCheckResult(**orjson.loads(c)) for c in row["all_checks"]],
            rule=rule,
            # data, check, labels
            # TS (timestamp)
        )
