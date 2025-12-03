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
from typing import Dict, Optional, List, Iterable, Tuple

# Third-party modules
from bson import ObjectId
from django.db.models.query_utils import Q as d_Q
from pymongo import UpdateOne
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
from noc.core.purgatorium import (
    ProtocolCheckResult,
    PurgatoriumData,
    iter_discovered_object,
    SOURCES,
    ETL_SOURCE,
)
from noc.core.mongo.fields import PlainReferenceField
from noc.config import config
from noc.core.ip import IP
from noc.main.models.pool import Pool
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.modeltemplate import (
    ResourceItem,
    DataItem as ResourceDataItem,
    CapsItem as ResourceCapsItem,
)
from noc.inv.models.capability import Capability
from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule
from noc.sa.models.managedobject import ManagedObject
from noc.wf.models.state import State

# Data source, data: Dict[str, str], source -> MergeRule[field-> policy]

logger = logging.getLogger(__name__)


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
    capabilities = DictField()
    event: str = StringField(required=False)
    is_delete: bool = BooleanField(default=False)  # Delete Flag

    def __str__(self):
        if self.remote_system:
            return f"{self.source}({self.last_update})@{self.remote_system.name}:{self.remote_id}: {','.join(self.data)}"
        return f"{self.source}({self.last_update}): {','.join(self.data)}"

    def __eq__(self, other: "DataItem") -> bool:
        if self.source != other.source:
            return False
        if other.remote_system and other.remote_system != self.remote_system:
            return False
        return self.data == other.data

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
@on_delete_check(clean=[("sa.DiscoveredObject", "origin")])
class DiscoveredObject(Document):
    meta = {
        "collection": "discoveredobjects",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["pool", "address"], "unique": True},
            {"fields": ["pool", "address_bin"]},
            {"fields": ["data.remote_system", "data.remote_id"]},
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
    is_dirty: bool = BooleanField(default=True)
    origin: Optional["DiscoveredObject"] = ReferenceField("self", required=False)
    # is_conflicted
    label = StringField()
    description = StringField()
    hostname = StringField()
    chassis_id = StringField()
    # Sources that find object,     timestamp: str = DateTimeField(required=True)
    sources: List[str] = ListField(StringField(choices=sorted(SOURCES)))
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
    agent: Optional["ObjectId"] = ObjectIdField(required=False)
    # Link to Rule
    rule: Optional["ObjectDiscoveryRule"] = PlainReferenceField(ObjectDiscoveryRule, required=False)
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
            labels += list(Label.merge_labels(self.extra_labels.values()))
        if not changed and set(self.effective_labels) == set(labels):
            return
        self.address_bin = IP.prefix(self.address).d
        self.is_dirty = True  # if data changed
        self.hostname = data.get("hostname")
        self.description = data.get("description")
        self.chassis_id = data.get("chassis_id")
        self.effective_data = data
        self.effective_labels = list(Label.merge_labels([labels], add_wildcard=True))
        # ToDO Rule Settings
        if self.hostname:
            self.duplicate_keys = [self.address_bin, bi_hash(self.hostname), *list(rids)]
        else:
            self.duplicate_keys = [self.address_bin, *list(rids)]

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

    def set_dirty(self, msg: Optional[str] = None):
        logger.debug("[%s] Set dirty %s", self.address, msg or "")
        self.is_dirty |= True

    def is_ttl(self, ts: Optional[datetime.datetime] = None) -> bool:
        if not self.rule.expired_ttl:
            return False
        now = datetime.date.today()
        ts = ts or self.last_seen
        return (now - ts.date()).seconds > self.rule.expired_ttl

    def change_rule(self, rule):
        self.rule = rule
        self.save()

    def refresh_rule(
        self, sources: Optional[List[str]] = None, rule: Optional[ObjectDiscoveryRule] = None
    ):
        """Check assigned rules on Object"""
        sources = sources or list(self.sources)
        rule = rule or self.get_rule(sources)
        if not rule:
            if self.rule and self.state:
                self.fire_event("expired")  # Remove
            logger.debug(
                "[%s|%s] Not find rule for address. Skipping", self.pool.name, self.address
            )
            return
        if self.rule != rule:
            logger.info(
                "[%s|%s] Update rule: %s -> %s",
                self.pool.name,
                self.address,
                self.rule.name if self.rule else "<empty>",
                rule.name,
            )
            self.rule = rule
            self.set_dirty("Update Rules")
        # Update sources
        sources = rule.merge_sources(sources)
        if list(self.sources) != sources:
            # Remove unused data
            for source in set(self.sources) - set(sources):
                self.reset_data(source)
            self.set_dirty("Update sources")
            self.sources = sources

    @classmethod
    def find_object_by_data(
        cls,
        address: str,
        pool: Pool,
        data: List[PurgatoriumData],
    ) -> List["DiscoveredObject"]:
        """Find Discovered object by data"""
        q = m_q(pool=pool, address=address)
        for d in data:
            if d.source == ETL_SOURCE and d.remote_system:
                rs = RemoteSystem.get_by_name(d.remote_system)
                q |= m_q(data__match={"remote_system": rs.id, "remote_id": d.data["remote_id"]})
        return list(DiscoveredObject.objects.filter(q))

    @classmethod
    def ensure_discovered_object(
        cls,
        sources: List[str],
        address: str,
        pool: Pool,
        data: List[PurgatoriumData],
        checks: Optional[List[ProtocolCheckResult]] = None,
        labels: Optional[List[str]] = None,
        rule: Optional[str] = None,
        update_ts: Optional[datetime.datetime] = None,
        dry_run: bool = False,
    ) -> Optional["DiscoveredObject"]:
        """Check Discovered Object Exists"""
        oo = cls.find_object_by_data(address, pool, data)
        if len(oo) == 1 and oo[0].address == address:
            # Replace pool ?
            o = oo[0]
        elif len(oo) == 1 and oo[0].address != address:
            # Moved address in ETL system
            o = None
        elif oo:
            # None ?
            o, data = cls.merge_discovered_objects(oo, address, data, dry_run=dry_run)
        else:
            o = None
        if not o:
            # Create
            o = DiscoveredObject(
                pool=pool,
                address=address,
                sources=sources,
                labels=labels or [],
                rule=rule,
            )
        # timestamp = timestamp or datetime.datetime.now()
        if not update_ts or update_ts != o.last_seen:
            if o.id:
                # For New object not logging
                logger.debug(
                    "[%s|%s] Run update data: %s/%s", pool.name, address, update_ts, o.last_seen
                )
            o.update_data(data, checks)  # Remove data
        return o

    @classmethod
    def merge_discovered_objects(
        cls,
        objects: List["DiscoveredObject"],
        address: str,
        data: List[PurgatoriumData],
        dry_run: bool = False,
    ) -> ["DiscoveredObject", List[PurgatoriumData]]:
        """
        get_moved object

        Merge Multiple Discovered Object when processed discovered
        When:
          * Changed device address on Remote System
          * When Change Device on Network (by hostname/mac)
        Do:
        1. When origin not Managed Object
         * Move only data and set is_dirty
        2. When origin and Destination with Managed Object
         * Move data and set is_dirty (apply changes on sync)
        3. When origin with ManagedObject and destination is not
         *

        """
        # Find origin record (by same IP)
        origin = None
        for o in objects:
            if o.address == address:
                origin = o
        # Current systems
        origin_rids = {
            (RemoteSystem.get_by_name(d.remote_system), d.remote_id): d.ts
            for d in data
            if d.source == ETL_SOURCE
        }
        # If not origin - New record, On other set delete_flag
        addresses, merged_rids, clean_rids = [], [], []
        for do in objects:
            if do.address == address:
                origin = do
                continue
            # set for moved
            for (rs, rid), ts in origin_rids.items():
                d = do.get_data(ETL_SOURCE, remote_system=rs)
                if not d:
                    continue
                if d.remote_id != rid:
                    continue
                if d.last_update > ts:
                    # Clean from Purgatorium Data
                    clean_rids.append((rs.name, rid))
                    continue
                # Set is_delete ? For Lost Deleted/by TTL
                merged_rids += do.reset_data(ETL_SOURCE, remote_system=rs)
            addresses.append(do.address)
            # Bulk Data ?
            if not dry_run:
                do.save()
        if merged_rids:
            logger.info(
                "[%s|%s|Merge] ETL Source moved from %s. Remote Ids: %s. Merge...",
                address,
                origin.rule if origin else "<new>",
                addresses,
                ",".join(merged_rids),
            )
        if clean_rids:
            logger.info(
                "[%s|%s|Merge] ETL Source on '%s' removed from own data. Remote Ids: %s. Merge...",
                address,
                origin.rule if origin else "<new>",
                addresses,
                ",".join(f"{x1}:{x2}" for x1, x2 in clean_rids),
            )
            return origin, [d for d in data if (d.remote_system, d.remote_id) not in clean_rids]
        return origin, data

    @classmethod
    def register(
        cls,
        pool: Pool,
        address: str,
        sources: List[str],
        data: List[PurgatoriumData],
        checks: Optional[List[ProtocolCheckResult]] = None,
        labels: Optional[List[str]] = None,
        update_ts: Optional[datetime.datetime] = None,
        rule=None,
        dry_run: bool = False,
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
            dry_run: Test run, not save changes
            rule:
        """
        if not isinstance(pool, Pool):
            pool = Pool.get_by_name(pool)
        o = DiscoveredObject.ensure_discovered_object(
            sources,
            address,
            pool,
            data,
            checks,
            labels,
            rule=rule,
            update_ts=update_ts,
            dry_run=dry_run,
        )
        o.refresh_rule(sources, rule=rule)
        if not o.is_dirty or rule:
            logger.debug("[%s|%s] Nothing updating data. Skipping", pool.name, address)
            return None
        if not o.rule and getattr(o, "_created"):
            return None
        if dry_run:
            logger.debug(
                "[%s|%s] Debug object: %s/%s/%s/%s", pool.name, address, sources, data, labels, rule
            )
            return o
        o.save()
        if update_ts and o.last_seen != update_ts:
            o.touch(ts=update_ts)
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
        data, mappings, caps, event = [], {}, [], None
        s_groups = set()
        for d in self.data:
            s = self.rule.get_sync_settings(d.source, d.remote_system)
            if s is None:
                continue
            if d.is_delete and s.remove_policy == "D":
                continue
            if d.is_delete:
                event = {"U": "unmanaged", "R": "remove"}[s.remove_policy]
            elif d.event:
                event = d.event
            if d.remote_system and d.remote_system not in mappings:
                mappings[d.remote_system] = d.remote_id
            if d.service_groups:
                s_groups.update(set(d.service_groups))
            if d.capabilities:
                caps.append(
                    ResourceCapsItem(
                        capabilities=d.capabilities,
                        remote_system=d.remote_system.name,
                    )
                )
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
                *data,
            ]
        r = ResourceItem(
            id=str(self.managed_object_id),
            labels=self.effective_labels,
            data=data,
            caps=caps or None,
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
            if self.is_preferred(d):
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
        return any(d.remote_system and d.remote_system.id == remote_system.id for d in self.data)

    def is_preferred(self, do: "DiscoveredObject") -> bool:
        """Compare DiscoveredObject"""
        if ETL_SOURCE not in do.sources:
            return len(self.sources) >= len(do.sources)
        for s in self.rule.sources:
            if not s.remote_system:
                continue
            if self.has_remote_system(s.remote_system) and not do.has_remote_system(
                s.remote_system
            ):
                return True
            if not self.has_remote_system(s.remote_system) and do.has_remote_system(
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
            if not mo.address:
                continue
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
            for m in mo.iter_remote_mappings():
                q |= m_q(
                    data__match={
                        "remote_id": m.remote_id,
                        "remote_system": m.remote_system.id,
                    }
                )
        if not q:
            return []
        return DiscoveredObject.objects.filter(id__ne=self.id).filter(q)

    def sync(self, dry_run: bool = False, force: bool = False, template=None, bulk=None):
        """Sync"""

        rule = self.get_rule(list(self.sources))
        if not rule:
            self.fire_event("expired")  # Remove
            # Unsync object
            if self.managed_object:
                self.managed_object.fire_event("unmanaged")
            self.is_dirty = False
            return
        if self.rule != rule:
            self.rule = rule
            self.save()
        action = rule.get_action(self.checks, self.effective_labels, self.effective_data)
        if dry_run:
            logger.info("[%s] Send action: %s", self.address, action)
        elif action == "ignore":
            self.fire_event("ignore")
        elif action == "approve":
            self.fire_event("approve")
        else:
            self.fire_event("seen")
        if self.is_approved or force:
            self.sync_object(dry_run=dry_run, template=template)
        if dry_run:
            return
        if bulk is not None:
            bulk += [UpdateOne({"_id": self.id}, {"$set": {"is_dirty": False}})]
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
            return None
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
        if not mo and template and not self.origin and ctx.data:
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
        capabilities: Optional[Dict[str, str]] = None,
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
            capabilities: Capabilities
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
            d.capabilities = capabilities
            d.labels = labels or []
            d.last_update = last_update
            d.is_delete = is_delete
            d.event = event
            self.set_dirty("Update data")
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
                    capabilities=capabilities,
                    last_update=last_update,
                    is_delete=is_delete,
                    event=event,
                )
            ]
            self.set_dirty("Add New Data")

    def get_data(
        self, source: str, remote_system: Optional[RemoteSystem] = None
    ) -> Optional[DataItem]:
        if source == ETL_SOURCE and not remote_system:
            raise AttributeError("")
        for item in self.data:
            if item.source != source and not remote_system:
                return item
            if remote_system and item.remote_system == remote_system:
                return item

    def reset_data(self, source: str, remote_system: Optional[RemoteSystem] = None):
        """
        Remove data for source or remote identifier
        Args:
            source: Input Source
            remote_system: Remote System
        """
        data, remote_rids = [], []
        for item in self.data:
            if item.source == source and not remote_system:
                continue
            if remote_system and not item.remote_system:
                continue
            if remote_system and item.remote_system.id == remote_system.id:
                remote_rids.append(item.remote_id)
                continue
            data.append(item)
        if len(data) != len(self.data):
            self.data = data
            self.is_dirty |= True
        return remote_rids

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
            caps = {}
            for c in d.caps or []:
                c_o = Capability.get_by_name(c)
                if not c_o:
                    logger.warning("Unknown capability: %s", c)
                    continue
                try:
                    caps[c] = c_o.clean_value(d.caps[c])
                except ValueError:
                    logger.warning("[%s] Bad value for caps: %s", c, caps[c])
                    continue
            # Check Update ts, if deleted
            self.set_data(
                d.source,
                d.data,
                d.labels,
                d.service_groups,
                d.client_groups,
                capabilities=caps,
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
            self.set_dirty("Update checks")

    def sync_object_data(
        self, ctx: ResourceItem, managed_object: Optional["ManagedObject"] = None, dry_run=False
    ) -> Optional[bool]:
        if not self.managed_object_id and not managed_object:
            logger.warning("Not exists ManagedObject. Skipping...")
            return
        if managed_object:
            mo = managed_object
        else:
            mo = ManagedObject.get_by_id(int(self.managed_object_id))
        if not mo:
            return
        if mo.id != self.managed_object_id:
            logger.info(
                "[%s] Update managed_object field to: %s", managed_object.name, managed_object.id
            )
        changed = False
        if mo.address != self.address:
            logger.info("Sync address to Discovered Object: %s -> %s", mo.address, self.address)
            mo.address = self.address
            changed |= True
        if mo.name != self.hostname:
            logger.info("Sync Name to Discovered Object: %s -> %s", mo.name, self.hostname)
            mo.name = self.hostname or f"{mo.address}#not_name"
            changed |= True
        if ctx.data and self.rule.default_template:
            changed |= self.rule.default_template.update_instance_data(mo, ctx, dry_run=True)
            if changed:
                logger.info("[%s] Update existing ManagedObject from data: %s", mo.name, ctx)
        # Mappings
        changed |= mo.update_remote_mappings(ctx.mappings or {})
        # Capabilities
        for cc in ctx.caps or []:
            mo.update_caps(
                cc.capabilities,
                source="etl",
                scope=cc.remote_system or "discovered",
                dry_run=False,
            )
        if dry_run:
            logger.info("Send signal (managed_object): %s", ctx.event or "managed")
            return
        if ctx.event == "duplicate":
            mo.fire_event("unmanaged")
            logger.info("Send duplicate signal (managed_object)")
        elif ctx.event:
            mo.fire_event(ctx.event)
        elif (
            not ctx.event
            and ETL_SOURCE in self.sources
            and not mo.remote_system
            and not ctx.has_rs_data()
        ):
            logger.info("[%s] Unsync ManagedObject, by lost master", mo.name)
            mo.fire_event("unmanaged")
        elif not ctx.event:
            mo.fire_event("managed")
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

    @classmethod
    def get_start_sync_ts(cls) -> datetime.datetime:
        """Getting Timestamp from started sync"""
        now = datetime.datetime.now()
        ls = DiscoveredObject.objects.filter().order_by("-last_seen").scalar("last_seen").first()
        ls = ls or now
        return ls - datetime.timedelta(seconds=config.network_scan.purgatorium_ttl)


def sync_object():
    """
    Sync Object with discovered records.
    Working with records with new and approved records with is_dirty flag
    1. Deduplicate
    2. Synchronize records with Agent and ManagedObject
    3. Synchronize data with ManagedObject
    """
    for do in DiscoveredObject.objects.filter(is_dirty=True):
        if do.rule.allow_sync and not do.origin and do.is_approved:
            do.sync()


def sync_purgatorium(
    disable_sync: bool = False, dry_run: bool = False, print_addresses: Optional[List[str]] = None
):
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
    """
    # Start timestamp
    ls_ex = DiscoveredObject.get_start_sync_ts()
    logger.info("Start Purgatorium sync from %s", ls_ex)
    processed, updated, removed, synced = 0, 0, 0, 0
    # Processed Discovered Objects
    for pool, address, sources, data, checks, last_ts in iter_discovered_object(ls_ex):
        if not address:
            continue
        pool = Pool.get_by_bi_id(pool)
        if print_addresses and address in print_addresses:
            logger.info("[%s] Data: %s", address, [str(d) for d in data])
        r = DiscoveredObject.register(
            pool,
            address,
            sources,
            data=data,
            checks=checks,
            update_ts=last_ts,
            dry_run=dry_run,
        )
        processed += 1
        if r:
            logger.debug("Updated: %s", r)
            updated += 1
    # Expired objects
    for o in DiscoveredObject.objects.filter(expired__gt=datetime.datetime.now()):
        o.fire_event("expired")
    logger.debug("Removing expired objects")
    # Removed objects
    for o in DiscoveredObject.objects.filter(state__in=list(State.objects.filter(is_wiping=True))):
        removed += 1
        o.delete()
    if disable_sync:
        logger.info(
            "End Purgatorium Sync: %s. Processed: %s/Updated: %s/Removed: %s/Synced: %s",
            ls_ex,
            processed,
            updated,
            removed,
            synced,
        )
        return
    # Sync objects and rules
    logger.info("Sync objects and rules")
    bulk = []
    coll = DiscoveredObject._get_collection()
    for do in DiscoveredObject.objects.filter(is_dirty=True, rule__exists=True):
        do.sync(bulk=bulk)
        if len(bulk) > 1000:
            coll.bulk_write(bulk)
            synced += len(bulk)
            bulk = []
    if bulk:
        coll.bulk_write(bulk)
        synced += len(bulk)
    logger.info(
        "End Purgatorium Sync: %s. Processed: %s/Updated: %s/Removed: %s/Synced: %s",
        ls_ex,
        processed,
        updated,
        removed,
        synced,
    )
