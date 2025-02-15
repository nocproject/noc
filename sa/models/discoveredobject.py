# ---------------------------------------------------------------------
# Discovered Object model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import itertools
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Optional, List, Any, Union, Iterable, Tuple

# Third-party modules
import orjson
from bson import ObjectId
from django.db.models.query_utils import Q as d_Q
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
from mongoengine.queryset.visitor import Q as m_q

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync, bi_hash
from noc.core.model.decorator import on_delete_check
from noc.core.clickhouse.connect import connection
from noc.core.purgatorium import ProtocolCheckResult, SOURCES, ETL_SOURCE
from noc.core.mongo.fields import PlainReferenceField
from noc.config import config
from noc.core.ip import IP
from noc.main.models.pool import Pool
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.modeltemplate import ResourceItem, DataItem as ResourceDataItem
from noc.inv.models.resourcegroup import ResourceGroup
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
    groupArray((source, remote_system,
        map('hostname', hostname, 'description', description, 'uptime', toString(uptime), 'remote_id', remote_id, 'ts', toString(max_ts)),
         data, labels, service_groups, clients_groups, is_delete)) as all_data,
    groupUniqArrayArray(checks) as all_checks,
    groupUniqArrayArray(labels) as all_labels,
    groupUniqArray(router_id) as router_ids,
    max(last_ts) as last_ts
FROM (
    SELECT ip, pool, remote_system, source,
     argMax(is_delete, ts) as is_delete,
     argMax(hostname, ts) as hostname, argMax(description, ts) as description,
     argMax(uptime, ts) as uptime, argMax(remote_id, ts) as remote_id, argMax(checks, ts) as checks,
     argMax(data, ts) as data, argMax(labels, ts) as labels,
     argMax(service_groups, ts) as service_groups, argMax(clients_groups, ts) as clients_groups,
     argMax(router_id, ts) as router_id, argMax(ts, ts) as max_ts, argMax(ts, ts) as last_ts
    FROM noc.purgatorium
    WHERE date >= %s
    GROUP BY ip, pool, remote_system, source
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
    service_groups: Optional[List[ObjectId]] = None
    client_groups: Optional[List[ObjectId]] = None
    data: Optional[Dict[str, str]] = None
    event: Optional[str] = None  # Workflow Event
    is_delete: bool = False  # Delete Flag

    def __str__(self):
        if self.remote_system:
            return f"{self.source}@{self.remote_system}: {self.data}"
        return f"{self.source}: {self.data}"

    @property
    def key(self) -> str:
        if not self.remote_system:
            return self.source
        return f"{self.source}@{self.remote_system}"


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
    service_groups: List[ObjectId] = ListField(ObjectIdField())
    client_groups: List[ObjectId] = ListField(ObjectIdField())
    data = DictField()
    event: str = StringField(required=False)
    is_delete: bool = BooleanField(default=False)  # Delete Flag

    def __str__(self):
        if self.remote_system:
            return (
                f"{self.source}#{self.remote_system.name}:{self.remote_id}: {','.join(self.data)}"
            )
        return f"{self.source}: {','.join(self.data)}"

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

    @property
    def key(self):
        if not self.remote_system:
            return self.source
        return f"{self.source}@{self.remote_system}"


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
            "origin",
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
    duplicate_keys = ListField(LongField())
    managed_object_id: Optional[int] = IntField(required=False)
    # Link to agent
    agent: "Agent" = ObjectIdField(required=False)
    # Link to Rule
    rule: "ObjectDiscoveryRule" = PlainReferenceField(ObjectDiscoveryRule, required=False)
    effective_data: Dict[str, str] = DictField()
    # Labels
    extra_labels: Dict[str, List[str]] = DictField()
    labels: List[str] = ListField(StringField())  # Manual Set
    effective_labels: List[str] = ListField(StringField())
    # Calculated duplicate hash
    # duplicate_hashes =
    # duplicate_keys =
    #
    bi_id = LongField(unique=True)
    # Comments ?

    PROFILE_LINK = "rule"
    IGNORED_SYNC_DATA = {"remote_id", "name", "description", "hostname", "address", "pool", "state"}

    def __str__(self):
        return f"{self.address}({self.pool})"

    def clean(self):
        """
        Sync data and labels
        rules - Merge/Update Rules
          * update data, for rules
            * field
            * source_priority
            * policy: set, replace, union (for list)
        :return:
        """
        data, labels, changed = {}, [], False
        rids = set()
        for di in self.iter_sorted_data():
            for key, value in di.data.items():
                if key in data or not value:
                    # Already set by priority source
                    continue
                data[key] = value
                if key not in self.effective_data or self.effective_data[key] != value:
                    changed = True
            if di.labels:
                labels += di.labels
            if di.remote_system:
                rids.add(bi_hash(f"{di.remote_system.id}{di.remote_id}"))
        changed |= bool(self.effective_data.keys() - data.keys())
        # Update Extra Labels
        if self.extra_labels:
            labels += [ll for ll in Label.merge_labels(self.extra_labels.values())]
        if not changed and set(self.effective_labels) == set(labels):
            return
        self.address_bin = IP.prefix(self.address).d
        self.is_dirty = True  # if data changed
        self.hostname = data.get("hostname")
        self.description = data.get("description")
        self.chassis_id = data.get("chassis_id")
        self.effective_data = data
        self.effective_labels = labels
        # ToDO Rule Settings
        if self.hostname:
            self.duplicate_keys = [self.address_bin, bi_hash(self.hostname)] + list(rids)
        else:
            self.duplicate_keys = [self.address_bin] + list(rids)

    @property
    def is_duplicate(self):
        """Check record is duplicate"""
        return self.origin and self.origin != self.id

    def iter_sorted_data(self, sources: Optional[List[str]] = None) -> Iterable["DataItem"]:
        """Return data sorted by source"""
        sources = sources or self.sources
        for di in sorted(
            itertools.filterfalse(lambda d: d.source not in self.sources, self.data),
            key=lambda x: sources.index(x.source),
        ):
            yield di

    def is_ttl(self, ts: Optional[datetime.datetime] = None) -> bool:
        if not self.rule.expired_ttl:
            return False
        now = datetime.date.today()
        ts = ts or self.last_seen
        return (now - ts.date()).seconds > self.rule.expired_ttl

    def change_rule(self, rule):
        self.rule = rule
        self.save()

    @classmethod
    def get_discovered_object_filter(
        cls,
        sources: List[str],
        address: str,
        pool: Pool,
        data: List[PurgatoriumData],
    ) -> m_q:
        """Build filter for discovered record"""
        q = m_q(pool=pool, address=address)
        if ETL_SOURCE not in sources:
            return q
        for d in data:
            if d.source == ETL_SOURCE and d.remote_system:
                rs = RemoteSystem.get_by_name(d.remote_system)
                q |= m_q(data__match={"remote_system": rs.id, "remote_id": d.data["remote_id"]})
        return q

    @classmethod
    def merge_discovered_object(
        cls,
        sources: List[str],
        address: str,
        pool: Pool,
        data: List[PurgatoriumData],
    ) -> Optional["DiscoveredObject"]:
        """Check ETL Source by RemoteSystem and RemoteId."""
        oo: List["DiscoveredObject"] = list(
            DiscoveredObject.objects.filter(
                cls.get_discovered_object_filter(sources, address, pool, data)
            )
        )
        if not oo:
            return None
        elif len(oo) == 1 and oo[0].address == address:
            return oo[0]
        elif len(oo) == 1:
            return None
        # Multiple instance - merge
        o = None
        moved_systems = {
            (d.remote_system, d.data["remote_id"]) for d in data if d.source == ETL_SOURCE
        }
        addresses = []
        # ETL Priority
        for do in oo:
            if do.address == address:
                o = do
                continue
            data = []
            for d in do.data:
                if d.source == ETL_SOURCE and (d.remote_system.name, d.remote_id) in moved_systems:
                    continue
                data.append(d)
            do.data = data
            addresses.append(do.address)
            do.save()
        logger.info("[%s] ETL Source moved from %s. Merge...", address, addresses)
        # Check origin
        return o

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
        Args:
            pool: Address Pool ? default
            address: Check Address
            sources: List available sources ?from data
            data: Source, labels, data
            checks: List of checks
            labels: Manual Set labels
            update_ts: Last update time
            rule:
        """
        if not isinstance(pool, Pool):
            pool = Pool.get_by_name(pool)
        o = cls.merge_discovered_object(sources, address, pool, data)
        # timestamp = timestamp or datetime.datetime.now()
        if not o:
            o = DiscoveredObject(
                pool=pool,
                address=address,
                sources=sources,
                labels=labels or [],
                rule=rule,
            )
        if not update_ts or update_ts != o.last_seen:
            if o.id:
                # For New object not logging
                logger.info(
                    "[%s|%s] Run update data: %s/%s", pool.name, address, update_ts, o.last_seen
                )
            o.update_data(data, checks)  # Remove data
        rule = rule or o.get_rule(sources)
        # if address == "10.98.254.131":
        #     logger.info("[%s|%s] Debug object: %s/%s/%s/%s", pool.name, address, sources, data, labels, rule)
        if not rule:
            if o.rule and o.state:
                o.fire_event("expired")  # Remove
            logger.debug("[%s|%s] Not find rule for address. Skipping", pool.name, address)
            return
        elif o.rule != rule:
            logger.info(
                "[%s|%s] Update rule: %s -> %s",
                pool.name,
                address,
                o.rule.name if o.rule else "<empty>",
                rule.name,
            )
            o.rule = rule
            o.is_dirty = True
        sources = rule.merge_sources(sources)
        if o.sources != sources:
            # Remove unused data
            for source in set(o.sources) - set(sources):
                o.reset_data(source)
            o.is_dirty = True
            o.sources = sources
        o.touch(ts=update_ts)
        if not o.is_dirty and rule == o.rule:
            logger.debug("[%s|%s] Nothing updating data. Skipping", pool.name, address)
            return
        o.save()
        return o

    def get_rule(self, sources: Optional[List[str]] = None) -> Optional["ObjectDiscoveryRule"]:
        """Get Discovered Object rule"""
        return ObjectDiscoveryRule.get_rule(
            self.address,
            self.pool,
            self.checks,
            self.data,
            sources or self.sources,
        )

    def get_ctx(self, is_new: bool = False) -> ResourceItem:
        """
        Getting Context for Synchronise object template
        Attrs:
            is_new: Flag create
        """
        data, mappings, event = [], {}, None
        s_groups = set()
        for d in self.data:
            s = self.rule.get_sync_settings(d.source, d.remote_system)
            if s is None:
                continue
            if d.is_delete and s.remove_policy == "D":
                continue
            elif d.is_delete:
                event = {"U": "unmanaged", "R": "remove"}[s.remove_policy]
            elif d.event:
                event = d.event
            if d.remote_system and d.remote_system not in mappings:
                mappings[d.remote_system] = d.remote_id
            if d.service_groups:
                s_groups.update(set(d.service_groups))
            if s.sync_policy == "M" and not is_new:
                continue
            for k, v in d.data.items():
                if k in self.IGNORED_SYNC_DATA:
                    continue
                data.append(
                    ResourceDataItem(
                        name=k,
                        value=v,
                        remote_system=str(d.remote_system.id) if d.remote_system else None,
                    )
                )
        if data:
            data = [
                ResourceDataItem(name="name", value=self.hostname),
                ResourceDataItem(name="description", value=self.description or ""),
                ResourceDataItem(name="hostname", value=self.hostname),
                ResourceDataItem(name="address", value=self.address),
                ResourceDataItem(name="pool", value=str(self.pool.id)),
            ] + data
        r = ResourceItem(
            id=str(self.managed_object_id),
            labels=self.effective_labels,
            data=data,
            event=event,
        )
        if mappings:
            r.mappings = mappings
        if s_groups:
            r.service_groups = list(s_groups)
        # Iter Origin
        # for o in DiscoveredObject.objects.filter(origin=self.id):
        #     if o.effective_labels:
        #         r.labels += o.effective_labels
        return r

    def merge_duplicates(
        self,
        duplicates: List["DiscoveredObject"],
        is_new: bool = False,
    ) -> Tuple["DiscoveredObject", ResourceItem]:
        """
        Merge Duplicates Record, and data
        1. If not ETL sources, set duplicate to origin
        2. If ETL source, compare preferred record
          * for preferred - replace origin
          * other - merge ctx data
        X for duplicates on multiple ETL Systems need weight for merge data
        """
        origin, origin_ctx = self, self.get_ctx(is_new=is_new)
        priority = [str(s.remote_system.id) for s in self.rule.sources if s.remote_system]
        for d in duplicates:
            if ETL_SOURCE not in d.sources:
                continue
            elif self.is_preferred(d):
                origin_ctx.merge_data(d.get_ctx(is_new=is_new), systems_priority=priority)
            else:
                origin = d
                # origin_ctx = d.get_ctx()
        if self.origin and self.id != origin.id:
            # Move to is_duplicate
            origin_ctx.event = "duplicate"
        return origin, origin_ctx

    def get_managed_object_query(
        self, pool: Optional[Pool] = None, addresses: Optional[List[str]] = None
    ):
        """Query for request Managed Object"""
        q = d_Q()
        if self.hostname:
            q |= d_Q(name__iexact=self.hostname)
        if pool:
            q |= d_Q(address=self.address, pool=pool)
        if addresses and pool:
            q |= d_Q(address__in=addresses, pool=pool)
        if ETL_SOURCE not in self.sources:
            return q
        for d in self.data:
            if d.remote_system:
                q |= d_Q(remote_system=d.remote_system, remote_id=d.remote_id)
                q |= d_Q(
                    mappings__contains=[
                        {"remote_system": str(d.remote_system.id), "remote_id": d.remote_id}
                    ]
                )
        return q

    def get_pool(self) -> Pool:
        """Return Address Pool"""
        pool = self.rule.get_pool(self.address)
        if not pool:
            pool = Pool.get_by_name("default")
        return pool

    def check_duplicate(
        self,
        hostname: Optional[str] = None,
        address: Optional[str] = None,
        managed_object: Optional[ManagedObject] = None,
    ) -> List["DiscoveredObject"]:
        """Check duplicate"""
        from noc.inv.models.subinterface import SubInterface
        from mongoengine.queryset.visitor import Q

        duplicate_keys = {self.address_bin}
        if address and address != self.address:
            duplicate_keys.add(IP.prefix(address).d)
        if hostname or self.hostname:
            duplicate_keys.add(bi_hash(hostname or self.hostname))
        # pool = self.pool
        if managed_object:
            # pool = managed_object.pool
            duplicate_keys.add(IP.prefix(managed_object.address).d)
            for d in SubInterface._get_collection().find(
                {"managed_object": managed_object.id, "ipv4_addresses": {"$exists": True}},
                {"ipv4_addresses": 1},
            ):
                for a in d.get("ipv4_addresses", []):
                    ip = IP.prefix(a)
                    if ip.is_loopback:
                        continue
                    duplicate_keys.add(ip.d)
        return DiscoveredObject.objects.filter(
            Q(origin=None, id__ne=self.id) & Q(duplicate_keys__in=list(duplicate_keys)),
        )

    def has_remote_system(self, remote_system: RemoteSystem) -> bool:
        """Check RemoteSystem in data"""
        for d in self.data:
            if d.remote_system and d.remote_system.id == remote_system.id:
                return True
        return False

    def is_preferred(self, do: "DiscoveredObject") -> bool:
        """Compare DiscoveredObject"""
        if ETL_SOURCE not in do.sources:
            return len(self.sources) >= len(do.sources)
        for s in self.rule.sources:
            if not s.remote_system:
                continue
            elif self.has_remote_system(s.remote_system) and not do.has_remote_system(
                s.remote_system
            ):
                return True
            elif not self.has_remote_system(s.remote_system) and do.has_remote_system(
                s.remote_system
            ):
                return False
        # ? RemoteSystem Count
        return len(self.sources) >= len(do.sources)

    def check_duplicates(self, mos: List["ManagedObject"]) -> List["DiscoveredObject"]:
        """Getting DiscoveredObject duplicates record by ManagedObjects"""
        from noc.inv.models.subinterface import SubInterface

        q = m_q()
        addresses = set()
        for mo in mos:
            addresses.add(IP.prefix(mo.address).address)
            # Pool
            for d in SubInterface._get_collection().find(
                {"managed_object": mo.id, "ipv4_addresses": {"$exists": True}},
                {"ipv4_addresses": 1},
            ):
                for a in d.get("ipv4_addresses", []):
                    ip = IP.prefix(a)
                    if ip.is_loopback:
                        continue
                    addresses.add(ip.address)
            q |= m_q(address__in=addresses)
            # if ETL_SOURCE not in self.sources:
            #    continue
            for m in mo.mappings:
                q |= m_q(
                    data__match={
                        "remote_id": m["remote_id"],
                        "remote_system": ObjectId(m["remote_system"]),
                    }
                )
        if not q:
            return []
        return DiscoveredObject.objects.filter(id__ne=self.id).filter(q)

    def sync(self, dry_run: bool = False, force: bool = False, template=None):
        """Sync"""

        rule = self.get_rule(list(self.sources))
        if not rule:
            # Unsync object
            self.fire_event("expired")  # Remove
            return
        elif self.rule != rule:
            self.rule = rule
            self.save()
        action = rule.get_action(self.checks, self.effective_labels, self.effective_data)
        if action == "ignore":
            self.fire_event("ignore")
        elif action == "approve":
            self.fire_event("approve")
        else:
            self.fire_event("seen")
        if self.is_approved or force:
            self.sync_object(dry_run=dry_run, template=template)
        if dry_run:
            return
        self.is_dirty = False
        DiscoveredObject.objects.filter(id=self.id).update(is_dirty=False)

    def fix_duplicate_managed_object(
        self,
        objects: List["ManagedObject"],
    ) -> Optional["ManagedObject"]:
        """Choice from multiple ManagedObject only own"""
        for o in objects:
            if o.name == self.hostname:
                return o
        for o in objects:
            if o.address == self.address:
                return o
        return objects[0]

    def sync_object(self, dry_run=False, template=None):
        """
        Sync with ManagedObject

        Args:
            dry_run: Run with test
            template: Sync object template
        """
        from noc.inv.models.discoveryid import DiscoveryID

        logger.debug("[%s] Sync Object", self)
        force = bool(template)
        template = template or self.rule.default_template
        if not template:
            logger.warning("[%s] Unknown Template for sync: %s", self, template)
            return
        # Getting ManagedObject
        pool = self.get_pool()
        q = self.get_managed_object_query(pool)
        objects = list(ManagedObject.objects.filter(q))
        if len(objects) > 1:
            # Fix duplicate objects
            mo = self.fix_duplicate_managed_object(objects)
            logger.warning(
                "[%s] Detect return multiple managedObject when sync: %s -> Fixed: %s",
                self.address,
                objects,
                mo,
            )
        elif len(objects) == 1:
            mo = objects[0]
        else:
            mo = DiscoveryID.find_object(ipv4_address=self.address, hostname=self.hostname)
        # Check duplicate Discovered Object
        duplicates = self.check_duplicates(objects)
        if duplicates:
            logger.info("[%s] Detect duplicate objects: %s", self.address, duplicates)
            origin, ctx = self.merge_duplicates(duplicates)
        else:
            origin, ctx = self.merge_duplicates(
                list(DiscoveredObject.objects.filter(origin=self)),
                is_new=force,
            )
        # Set origin
        if self.id != origin.id:
            self.origin = origin
        elif self.origin:
            self.origin = None
        # Check policy
        if not mo and template and not self.origin:
            # Create New
            mo = template.render(ctx)
        elif not mo and not template:
            raise AttributeError("Default object template is not Set")
        if dry_run:
            logger.info("[%s] Origin record: %s", self.address, origin)
            self.sync_object_data(ctx, managed_object=mo, dry_run=dry_run)
            return mo
        if mo and not mo.id:
            # Save new
            mo.save()
        elif mo and not self.origin:
            self.sync_object_data(ctx, managed_object=mo, dry_run=dry_run)
        # Update fields
        # Send unmanaged to ManagedObject ?
        mo_id = mo.id if mo else None
        if mo_id != self.managed_object_id:
            self.managed_object_id = mo_id
            DiscoveredObject.objects.filter(id=self.id).update(
                # is_dirty=self.is_dirty,
                managed_object_id=self.managed_object_id,
                origin=self.origin,
            )
            DiscoveredObject.objects.filter(origin=self.origin, is_dirty=False).update(
                is_dirty=True,
            )
        elif self.id != origin.id:
            DiscoveredObject.objects.filter(id=self.id).update(
                origin=self.origin,
            )
        # duplicates = [d.id for d in duplicates if d != origin]
        # if duplicates:
        #     DiscoveredObject.objects.filter(id__in=duplicates).update(is_dirty=True, origin=origin)
        #     DiscoveredObject.objects.filter(id__nin=duplicates, origin=origin).update(is_dirty=True, origin=None)
        # # Send sync
        if ctx.event == "duplicate":
            self.fire_event("duplicate")
        elif not mo:
            self.fire_event("revoke")
        else:
            self.fire_event("synced")

    @property
    def is_approved(self) -> bool:
        if not self.rule:
            return False
        if not self.managed_object_id and not self.rule.sync_approved:
            return False
        return self.state.is_productive

    def set_data(
        self,
        source,
        data: Dict[str, str],
        labels: Optional[List[str]] = None,
        service_groups: Optional[List[ObjectId]] = None,
        client_groups: Optional[List[ObjectId]] = None,
        remote_system: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
        event: str = False,
        is_delete: bool = False,
    ):
        """
        Set data for source

        Args:
            source: Source code
            data: Dict of data
            labels: label list
            service_groups: Service groups
            client_groups: Client groups
            remote_system: Remote System from data
            ts: timestamp when data updated
            event: Workflow Event on RemoteSystem
            is_delete: Flag if record deleted on source
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
                break
            if set(service_groups or []) != set(d.service_groups or []):
                d.service_groups = service_groups
            if set(client_groups or []) != set(d.client_groups or []):
                d.client_groups = client_groups
            d.data = data
            d.labels = labels or []
            d.last_update = last_update
            d.is_delete = is_delete
            d.event = event
            self.is_dirty = True
            break
        else:
            self.data += [
                DataItem(
                    source=source,
                    remote_system=remote_system,
                    remote_id=data.pop("remote_id", None),
                    labels=labels,
                    service_groups=service_groups,
                    client_groups=client_groups,
                    data=data,
                    last_update=last_update,
                    is_delete=is_delete,
                )
            ]
            self.is_dirty = True

    def reset_data(self, source, remote_id: Optional[str] = None):
        self.data = [
            item
            for item in self.data
            if (item.source != source and not remote_id)
            or (remote_id and item.remote_id != remote_id)
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
        Args:
            data:
            checks: List processed checks
        """
        processed_keys = set()
        # Merge Data
        for d in data:
            if d.source not in self.sources:
                # @todo Skip data if not in source
                continue
            rs = None
            if d.remote_system:
                rs = RemoteSystem.get_by_name(d.remote_system)
            self.set_data(
                d.source,
                d.data,
                d.labels,
                d.service_groups,
                d.client_groups,
                remote_system=rs,
                ts=d.ts,
                is_delete=d.is_delete,
                event=d.event,
            )
            processed_keys.add(d.key)
        # Clear lost data
        self.data = [d for d in self.data if d.key in processed_keys]
        if not (checks or self.checks):
            return
        checks = [
            CheckStatus(name=c.check, status=c.status, port=c.port, error=c.error) for c in checks
        ]
        if not self.checks or set(self.checks).symmetric_difference(set(checks)):
            self.checks = checks
            self.is_dirty |= True

    def sync_object_data(
        self, ctx: ResourceItem, managed_object: Optional["ManagedObject"] = None, dry_run=False
    ) -> Optional[bool]:
        if not self.managed_object_id and not managed_object:
            logger.warning("Not exists ManagedObject. Skipping...")
            return
        elif managed_object:
            logger.info(
                "[%s] Update managed_object field to: %s", managed_object.name, managed_object.id
            )
            mo = managed_object
        else:
            mo = ManagedObject.get_by_id(int(self.managed_object_id))
        if not mo:
            return
        changed = False
        if mo.address != self.address:
            logger.info("Sync address to Discovered Object: %s -> %s", mo.address, self.address)
            mo.address = self.address
            changed |= True
        if mo.name != self.hostname:
            logger.info("Sync Name to Discovered Object: %s -> %s", mo.name, self.hostname)
            mo.name = self.hostname
            changed |= True
        if ctx.data and self.rule.default_template:
            changed |= self.rule.default_template.update_instance_data(mo, ctx, dry_run=True)
            if changed:
                logger.info("[%s] Update existing ManagedObject from data: %s", mo.name, ctx)
        changed |= mo.update_object_mappings(ctx.mappings or {})
        if dry_run:
            return
        if ctx.event == "duplicate":
            mo.fire_event("unmanaged")
            logger.info("Send duplicate signal (managed_object)")
        elif ctx.event:
            mo.fire_event(ctx.event or "managed")
        elif (
            not ctx.event
            and ETL_SOURCE in self.sources
            and not mo.remote_system
            and not ctx.has_rs_data()
        ):
            logger.info("[%s] Unsync ManagedObject, by lost master", mo.name)
            mo.fire_event("unmanaged")
        if changed:
            mo.save()

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        if not self.managed_object_id:
            return None
        o = ManagedObject.get_by_id(self.managed_object_id)
        if not o:
            logger.info(
                "[%s] Not found ManagedObject by id '%s'. Unset attribute",
                self.address,
                self.managed_object_id,
            )
            DiscoveredObject.objects.filter(id=self.id).update(unset__managed_object_id=1)
            self.fire_event("revoke")
            o.save()
        return o


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
        if do.rule.allow_sync and not do.origin and do.is_approved:
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
    ls = (
        DiscoveredObject.objects.filter().order_by("-last_seen").scalar("last_seen").first()
        or datetime.datetime.now()
    )
    ls_ex = ls - datetime.timedelta(seconds=config.network_scan.purgatorium_ttl)
    logger.info("Start Purgatorium Sync: %s, Expired: %s", ls, ls_ex)
    ranges = defaultdict(list)
    # ranges filter
    for r in ObjectDiscoveryRule.objects.filter(is_active=True):
        for p in r.get_prefixes():
            ranges[p].append(r)
    ch = connection()
    r = ch.execute(PURGATORIUM_SQL, return_raw=True, args=[ls_ex.date().isoformat()])
    processed, updated, removed, synced = 0, 0, 0, 0
    # New records
    for num, row in enumerate(r.splitlines(), start=1):
        row = orjson.loads(row)
        pool = Pool.get_by_bi_id(row["pool"])
        data = defaultdict(dict)
        d_labels = defaultdict(list)
        groups = defaultdict(list)
        # hostnames, descriptions, uptimes, all_data,
        for source, rs, d1, d2, labels, s_groups, c_groups, is_delete in row["all_data"]:
            if is_delete:
                logger.debug("[%s] Detect deleted flag", row["address"])
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
            data[(source, rs)]["is_delete"] = bool(is_delete)
            d_labels[(source, rs)] = labels
            for rg in s_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "s")].append(rg.id)
            for rg in c_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "c")].append(rg.id)
        last_ts = datetime.datetime.fromisoformat(row["last_ts"]).replace(microsecond=0)
        r = DiscoveredObject.register(
            pool,
            row["address"],
            list(set(row["sources"])),
            data=[
                PurgatoriumData(
                    source=source,
                    ts=datetime.datetime.fromisoformat(d.pop("ts")),
                    remote_system=rs,
                    data=d,
                    labels=d_labels.get((source, rs)) or [],
                    service_groups=groups.get((source, rs, "s")) or [],
                    client_groups=groups.get((source, rs, "c")) or [],
                    is_delete=bool(d.pop("is_delete")),
                    event=d.pop("event", None),
                )
                for (source, rs), d in data.items()
            ],
            checks=[ProtocolCheckResult(**orjson.loads(c)) for c in row["all_checks"]],
            update_ts=last_ts,
            # data, check, labels
            # TS (timestamp)
        )
        processed += 1
        if r:
            logger.debug("Updated: %s", r)
            updated += 1
    now = datetime.datetime.now()
    # Expired objects
    for o in DiscoveredObject.objects.filter(expired__gt=now):
        o.fire_event("expired")
    logger.debug("Removing expired objects")
    # Removed objects
    for o in DiscoveredObject.objects.filter(state__in=list(State.objects.filter(is_wiping=True))):
        removed += 1
        o.delete()
    # Sync objects and rules
    logger.info("Sync objects and rules")
    for do in DiscoveredObject.objects.filter(is_dirty=True, rule__exists=True):
        do.sync()
        # DiscoveredObject.objects.filter(id=do.id).update(is_dirty=False)
    logger.info(
        "End Purgatorium Sync: %s. Processed: %s/Updated: %s/Removed: %s/Synced: %s",
        ls,
        processed,
        updated,
        removed,
        synced,
    )
