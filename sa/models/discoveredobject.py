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
from typing import Dict, Optional, List, Any, Union, Tuple

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

# NOC modules
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync, bi_hash
from noc.core.model.decorator import on_delete_check
from noc.core.clickhouse.connect import connection
from noc.core.purgatorium import ProtocolCheckResult, SOURCES, ETL_SOURCE
from noc.core.mongo.fields import PlainReferenceField
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
    groupArray((source, remote_system, map('hostname', hostname, 'description', description, 'uptime', toString(uptime), 'remote_id', remote_id, 'ts', toString(max_ts)), data, labels, service_groups, clients_groups)) as all_data,
    groupUniqArrayArray(checks) as all_checks,
    groupUniqArrayArray(labels) as all_labels,
    groupUniqArray(router_id) as router_ids,
    max(last_ts) as last_ts
FROM (
    SELECT ip, pool, remote_system, source,
     argMax(hostname, ts) as hostname, argMax(description, ts) as description,
     argMax(uptime, ts) as uptime, argMax(remote_id, ts) as remote_id, argMax(checks, ts) as checks,
     argMax(data, ts) as data, argMax(labels, ts) as labels,
     argMax(service_groups, ts) as service_groups, argMax(clients_groups, ts) as clients_groups,
     argMax(router_id, ts) as router_id, argMax(ts, ts) as max_ts, argMax(ts, ts) as last_ts
    FROM noc.purgatorium
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

    def __str__(self):
        if self.remote_system:
            return f"{self.source}@{self.remote_system}: {self.data}"
        return f"{self.source}: {self.data}"


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
    #
    duplicate_keys = ListField(LongField())
    #
    managed_object_id: int = IntField(required=False)
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
    # duplicate_hashes =
    # duplicate_keys =
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
            * policy: set, replace, union (for list)
        :return:
        """
        #
        data, labels, changed = {}, [], False
        rids = set()
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
            if di.remote_system:
                rids.add(bi_hash(f"{di.remote_system.id}{di.remote_id}"))
        # Update Extra Labels
        if self.extra_labels:
            labels += [ll for ll in Label.merge_labels(self.extra_labels.values())]
        # if not changed and set(self.effective_labels) == set(labels):
        #    return
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
        elif set(o.sources).symmetric_difference(set(sources)):
            o.sources = sources
            o.is_dirty = True
        if not update_ts or update_ts != o.last_seen:
            logger.debug("[%s|%s] Run update data", pool.name, address)
            o.update_data(data, checks)
        rule = rule or ObjectDiscoveryRule.get_rule(
            address,
            pool,
            o.checks,
            o.effective_labels,
            o.get_effective_data(),
            sources,
        )
        if not rule:
            if o.rule and o.state:
                o.fire_event("expired")  # Remove
            logger.debug("[%s|%s] Not find rule for address. Skipping", pool.name, address)
            return
        if not o.is_dirty and rule == o.rule:
            logger.debug("[%s|%s] Nothing updating data. Skipping", pool.name, address)
            return
        if o.rule != rule:
            o.rule = rule
            o.is_dirty = True
        action = rule.get_action(o.checks, o.effective_labels, o.get_effective_data())
        if action == "skip":
            return
        elif action == "ignore" and not o.id:
            return
        if not o.id or o.is_dirty:
            # Set Status, is_dirty
            o.is_dirty = False
            o.save()
        o.fire_event("seen")
        o.touch(ts=update_ts)
        if action == "ignore":
            o.fire_event("ignore")
        elif action == "approve":
            o.fire_event("approve")
        return o

    def get_ctx(self) -> ResourceItem:
        """
        Getting Context for Synchronise object template
        """
        r = ResourceItem(
            id=str(self.managed_object_id),
            labels=self.effective_labels,
            data=[
                ResourceDataItem(name="name", value=self.hostname),
                ResourceDataItem(name="description", value=self.description),
                ResourceDataItem(name="hostname", value=self.hostname),
                ResourceDataItem(name="address", value=self.address),
                ResourceDataItem(name="pool", value=str(self.pool.id)),
            ],
        )
        mappings = {}
        s_groups = set()
        for d in self.data:
            for k, v in d.data.items():
                r.data.append(
                    ResourceDataItem(
                        name=k,
                        value=v,
                        remote_system=str(d.remote_system.id) if d.remote_system else None,
                    )
                )
            if d.remote_system and d.remote_system not in mappings:
                mappings[d.remote_system] = d.remote_id
            if d.service_groups:
                s_groups.update(set(d.service_groups))
        if mappings:
            r.mappings = mappings
        if s_groups:
            r.service_groups = list(s_groups)
        # Iter Origin
        for o in DiscoveredObject.objects.filter(origin=self.id):
            if o.effective_labels:
                r.labels += o.effective_labels
        return r

    def get_managed_object_query(
        self, pool: Optional[Pool] = None, addresses: Optional[List[str]] = None
    ):
        """Query for request Managed Object"""
        q = d_Q(name=self.hostname)
        if pool:
            q |= d_Q(address=self.address, pool=pool)
        if addresses and pool:
            q |= d_Q(address__in=addresses, pool=pool)
        for d in self.data:
            if d.remote_system:
                q |= d_Q(remote_system=d.remote_system, remote_id=d.remote_id)
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

    def sync(self, dry_run=False):
        """
        Sync with ManagedObject

        Args:
            dry_run: Run with test
        """
        from noc.inv.models.discoveryid import DiscoveryID

        if self.origin:
            logger.info("Duplicate Record. Skipping")
            return
        if not self.rule.default_template:
            return
        if self.managed_object_id:
            # Sync data
            self.sync_object_data(dry_run=dry_run)
            return
        # Create Managed Object instance
        pool = self.get_pool()
        duplicates = self.check_duplicate()
        # Check Removed Managed Object ?
        mo = ManagedObject.objects.filter(
            self.get_managed_object_query(pool, addresses=[di.address for di in duplicates]),
        ).first()
        if not mo:
            mo = DiscoveryID.find_object(ipv4_address=self.address, hostname=self.hostname)
        if mo:
            duplicates = self.check_duplicate(managed_object=mo)
        elif not mo and self.rule.default_template:
            mo = self.rule.default_template.render(self.get_ctx())
        else:
            raise AttributeError("Default object template is not Set")
        origin = self
        for di in duplicates:
            if di.address == mo.address:
                origin = di
        if dry_run:
            logger.info("[%s] Origin is: %s", self, origin)
            return mo
        if not mo.id:
            mo.save()
        else:
            origin.sync_object_data(managed_object=mo, dry_run=dry_run)
        if not origin.managed_object_id or origin.managed_object_id != mo.id:
            origin.managed_object_id = mo.id
            DiscoveredObject.objects.filter(id=origin.id).update(
                is_dirty=origin.is_dirty,
                managed_object_id=origin.managed_object_id,
            )
        # Update Origin
        duplicates = [d.id for d in duplicates if d != origin]
        if origin.id != self.id:
            duplicates.append(self.id)
            self.origin = origin
        if duplicates:
            DiscoveredObject.objects.filter(id__in=duplicates).update(is_dirty=True, origin=origin)
        origin.is_dirty = False
        # Send approve

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
        service_groups: Optional[List[ObjectId]] = None,
        client_groups: Optional[List[ObjectId]] = None,
        remote_system: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
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
            if set(service_groups or []) != set(d.service_groups or []):
                d.service_groups = service_groups
            if set(client_groups or []) != set(d.client_groups or []):
                d.client_groups = client_groups
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
                    service_groups=service_groups,
                    client_groups=client_groups,
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
        Args:
            data:
            checks: List processed checks
        """
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
            )
        if not checks and not self.checks:
            return
        checks = [
            CheckStatus(name=c.check, status=c.status, port=c.port, error=c.error) for c in checks
        ]
        if not self.checks or set(checks).difference(set(checks)):
            self.checks = checks
            self.is_dirty = True

    def sync_object_data(
        self, managed_object: Optional["ManagedObject"] = None, dry_run=False
    ) -> Optional[bool]:
        if not self.managed_object_id and not managed_object:
            logger.warning("Not exists ManagedObject. Skipping...")
            return
        elif not self.managed_object_id and managed_object:
            logger.info(
                "[%s] Update managed_object field to: %s", managed_object.name, managed_object.id
            )
            if not dry_run:
                DiscoveredObject.objects.filter(id=self.id).update(
                    is_dirty=self.is_dirty,
                    managed_object=managed_object.id,
                )
            mo = managed_object
        else:
            mo = ManagedObject.get_by_id(int(self.managed_object_id))
        if mo and self.rule.default_template and not dry_run:
            logger.info("[%s] Update existing ManagedObject from data", mo.name)
            self.rule.default_template.update_instance_data(mo, self.get_ctx(), dry_run=dry_run)

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        if not self.managed_object_id:
            return None
        return ManagedObject.get_by_id(self.managed_object_id)


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
    ls = DiscoveredObject.objects.filter().order_by("-last_seen").scalar("last_seen").first()
    logger.info("Start Purgatorium Sync: %s", ls)
    ranges = defaultdict(list)
    # ranges filter
    for r in ObjectDiscoveryRule.objects.filter(is_active=True):
        for p in r.get_prefixes():
            ranges[p].append(r)
    ch = connection()
    r = ch.execute(PURGATORIUM_SQL, return_raw=True)
    processed, updated, removed, synced = 0, 0, 0, 0
    for row in r.splitlines():
        row = orjson.loads(row)
        pool = Pool.get_by_bi_id(row["pool"])
        data = defaultdict(dict)
        d_labels = defaultdict(list)
        groups = defaultdict(list)
        # hostnames, descriptions, uptimes, all_data,
        for source, rs, d1, d2, labels, s_groups, c_groups in row["all_data"]:
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
            #
            d_labels[(source, rs)] = labels
            #
            for rg in s_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "s")].append(rg.id)
            for rg in c_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "c")].append(rg.id)
        last_ts = datetime.datetime.fromisoformat(row["last_ts"])
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
    # Sync objects
    for do in DiscoveredObject.objects.filter(is_dirty=True, rule__exists=True):
        if do.rule.allow_sync and do.rule.default_template and not do.origin and do.is_approved:
            do.sync()
    logger.info(
        "End Purgatorium Sync: %s. Processed: %s/Updated: %s/Removed: %s/Synced: %s",
        ls,
        processed,
        updated,
        removed,
        synced,
    )
