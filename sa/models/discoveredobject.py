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
    ObjectIdField,
)

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.core.clickhouse.connect import connection
from noc.core.purgatorium import ProtocolCheckResult, SOURCES, ETL_SOURCE
from noc.core.mongo.fields import PlainReferenceField
from noc.core.ip import IP
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
    groupUniqArrayArray(labels) as all_labels,
    max(last_ts) as last_ts
FROM (
    SELECT ip, pool, remote_system,
     argMax(source, ts) as source, argMax(hostname, ts) as hostname, argMax(description, ts) as description,
     argMax(uptime, ts) as uptime, argMax(remote_id, ts) as remote_id, argMax(checks, ts) as checks,
     argMax(data, ts) as data, argMax(labels, ts) as labels, argMax(ts, ts) as max_ts,
     argMax(ts, ts) as last_ts
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
    ts: Optional[datetime.datetime] = None
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

    def __hash__(self):
        return hash((self.name, self.port or 0, self.arg0 or "", self.status))

    def check_condition(self):
        """

        :return:
        """


class DataItem(EmbeddedDocument):
    source: str = StringField(required=True)
    last_update = DateTimeField(required=False)
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
@on_delete_check(check=[("sa.DiscoveredObject", "origin")])
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
    managed_object: "ManagedObject" = IntField(required=False)
    # Link to agent
    agent: "Agent" = ObjectIdField(required=False)
    # Link to Rule
    rule: "ObjectDiscoveryRule" = PlainReferenceField(ObjectDiscoveryRule, required=False)
    #
    effective_data: Dict[str, str] = DictField()
    # Labels
    extra_labels: Dict[str, List[str]] = DictField()
    labels: List[str] = ListField(StringField())  # Manual Set
    effective_labels: List[str] = ListField(StringField())
    # Calculated duplicate hash
    # duplicate_hash =
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
        update_ts: Optional[datetime.datetime] = None,
        rule=None,  # Processed rule
    ) -> Optional["DiscoveredObject"]:  # MergeRule
        """
        Register New record
        1. Ensure Discovery Object
        2. Update Data obj.update_data
        3. Rules = for merge data
        4. is_dirty = True if data changed
        :param pool: Address Pool ? default
        :param address: Check Address
        :param sources: List available sources ?from data
        :param data: Source, labels, data
        :param checks: List of checks
        :param labels: Manual Set labels
        :param update_ts: Last update time
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
        rule = rule or ObjectDiscoveryRule.get_rule(address, pool, checks)
        if not rule:
            logger.debug("[%s|%s] Not find rule for address. Skipping", pool.name, address)
            return
        if update_ts and update_ts == o.last_seen and rule == o.rule:
            logger.info("[%s|%s] Nothing updating data. Skipping", pool.name, address)
            return
        if o.rule != rule:
            o.rule = rule
            o.is_dirty = True
        if set(o.sources).difference(set(sources)):
            o.sources = sources
            o.is_dirty = True
        # Set Status, is_dirty
        o.update_data(data, checks)
        o.save()
        o.fire_event(rule.action)
        o.touch(ts=update_ts)
        return o

    def sync(self):
        """
        Sync with ManagedObject or Agent
        :return:
        """
        ctx = {
            "hostname": self.hostname,
            "description": self.description,
            "address": self.address,
            "effective_labels": self.effective_labels,
        }
        ctx |= self.effective_data
        if self.managed_object:
            # Sync data
            mo = ManagedObject.objects.filter(id=self.managed_object).first()
        else:
            # Check Removed Managed Object ?
            pool = self.rule.get_pool(self.address)
            # Check duplicate
            mo = ManagedObject.objects.filter(address=self.address, pool=pool).first()
            if not mo:
                mo = ManagedObject.get_object_by_template(
                    address=self.address, pool=pool, name=self.hostname
                )
        mo.update_template_data(ctx)
        mo.save()
        self.managed_object = mo.id
        self.is_dirty = False
        # Send approve
        DiscoveredObject.objects.filter(id=self.id).update(
            is_dirty=self.is_dirty,
            managed_object=self.managed_object,
        )

    @property
    def is_approved(self) -> bool:
        if not self.rule:
            return False
        return self.state.is_productive

    def set_data(
        self,
        source,
        data: Dict[str, str],
        labels: Optional[List[str]] = None,
        remote_system: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        """
        Set data for source
        :param source: Source code
        :param data: Dict of data
        :param labels: label list
        :param remote_system: Remote System from data
        :param ts: timestamp when data updated
        :return:
        """
        if source == ETL_SOURCE and not remote_system:
            raise AttributeError("remote_system param is required for 'etl' source")
        last_update = ts or datetime.datetime.now().replace(microsecond=0)
        for d in self.data:
            if d.source != source:
                continue
            if remote_system and remote_system != d.remote_system:
                continue
            if d.last_update == last_update:
                continue
            d.data = data
            d.labels = labels or []
            d.last_update = last_update
            break
        else:
            self.data += [
                DataItem(
                    source=source,
                    remote_system=remote_system,
                    remote_id=data.pop("remote_id", None),
                    labels=labels,
                    data=data,
                    last_update=last_update,
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
                # @todo Skip data if not in source
                continue
            rs = None
            if d.remote_system:
                rs = RemoteSystem.get_by_name(d.remote_system)
            self.set_data(d.source, d.data, d.labels, remote_system=rs)
        if not checks and not self.checks:
            return
        checks = [
            CheckStatus(name=c.check, status=c.status, port=c.port, error=c.error) for c in checks
        ]
        if not self.checks or set(checks).difference(set(checks)):
            self.checks = checks
            self.is_dirty = True


def sync_object():
    """
    Sync Object with discovered records.
    Working with records with new and approved records with is_dirty flag
    1. Deduplicate
    2. Synchronize records with Agent and ManagedObject
    3. Synchronize data with ManagedObject
    :return:
    """
    for do in DiscoveredObject.objects.filter(is_dirty=True):
        if do.rule.allow_sync and not do.origin:
            do.sync()


def sync_purgatorium():
    """
    Sync Discovered records with Purgatorium
    1. Load by CHUNK from Purgatorium
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
    ls = DiscoveredObject.objects.filter().order_by("-last_seen").scalar("last_seen").first()
    logger.info("Start Purgatorium Sync: %s", ls)
    ranges = defaultdict(list)
    # ranges filter
    for r in ObjectDiscoveryRule.objects.filter(is_active=True):
        for p in r.get_prefixes():
            ranges[p].append(r)
    ch = connection()
    r = ch.execute(PURGATORIUM_SQL, return_raw=True)
    for row in r.splitlines():
        row = orjson.loads(row)
        pool = Pool.get_by_bi_id(row["pool"])
        data = defaultdict(dict)
        # hostnames, descriptions, uptimes, all_data,
        for source, rs, d1, d2, labels in row["all_data"]:
            if not int(d1["uptime"]):
                # Filter 0 uptime
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
        last_ts = datetime.datetime.fromisoformat(row["last_ts"])
        DiscoveredObject.register(
            pool,
            row["address"],
            list(set(row["sources"])),
            data=[
                PurgatoriumData(
                    source=source,
                    ts=datetime.datetime.fromisoformat(d.pop("ts")),
                    remote_system=rs,
                    data=d,
                )
                for (source, rs), d in data.items()
            ],
            checks=[ProtocolCheckResult(**orjson.loads(c)) for c in row["all_checks"]],
            update_ts=last_ts,
            # data, check, labels
            # TS (timestamp)
        )
    now = datetime.datetime.now()
    for o in DiscoveredObject.objects.filter(expired__gt=now):
        o.fire_event("expired")
