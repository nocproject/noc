# ---------------------------------------------------------------------
# Network Segment
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import cachetools
from threading import Lock
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    DictField,
    ReferenceField,
    ListField,
    BooleanField,
    IntField,
    EmbeddedDocumentField,
    LongField,
)
from django.db.models.aggregates import Count
from pymongo.errors import OperationFailure

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.topology.types import TopologyNode
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.model.decorator import on_delete_check, on_save, tree
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync
from noc.core.scheduler.job import Job
from noc.core.cache.base import cache
from noc.vc.models.vlanfilter import VLANFilter
from noc.vc.models.vlan import VLAN
from noc.vc.models.l2domain import L2Domain
from .networksegmentprofile import NetworkSegmentProfile
from .allocationgroup import AllocationGroup
from .link import Link

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=100, ttl=60)


class VLANTranslation(EmbeddedDocument):
    filter = ReferenceField(VLANFilter)
    rule = StringField(
        choices=[
            # Rewrite tag to parent vlan's
            ("map", "map"),
            # Append parent tag as S-VLAN
            ("push", "push"),
        ],
        default="push",
    )
    parent_vlan = ReferenceField(VLAN)


@tree()
@bi_sync
@change
@on_delete_check(
    check=[
        ("sa.AdministrativeDomain", "bioseg_floating_parent_segment"),
        ("sa.ManagedObject", "segment"),
        ("inv.NetworkSegment", "parent"),
        ("inv.NetworkSegment", "sibling"),
    ]
)
@on_save
class NetworkSegment(Document):
    meta = {
        "collection": "noc.networksegments",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "sibling", "adm_domains"],
    }

    name = StringField(unique=True)
    parent = ReferenceField("self", required=False)
    profile = ReferenceField(NetworkSegmentProfile, required=True)
    description = StringField(required=False)
    # Management VLAN processing order
    # * d - disable management vlan
    # * e - enable management vlan and get from management_vlan field
    # * p - use profile settings
    management_vlan_policy = StringField(
        choices=[("d", "Disable"), ("p", "Profile"), ("e", "Enable")], default="p"
    )
    management_vlan = IntField(required=False, min_value=1, max_value=4095)
    # MVR VLAN processing order
    # * d - disable multicast vlan
    # * e - enable multicast vlan and get from multicast_vlan field
    # * p - use profile settings
    multicast_vlan_policy = StringField(
        choices=[("d", "Disable"), ("p", "Profile"), ("e", "Enable")], default="p"
    )
    multicast_vlan = IntField(required=False, min_value=1, max_value=4095)

    settings = DictField(default=lambda: {}.copy())
    labels = ListField(StringField())
    l2_domain = ReferenceField(L2Domain, required=False)
    # Sibling segment, if part of larger structure with
    # horizontal links
    sibling = ReferenceField("self")
    # True if segment has alternative paths
    is_redundant = BooleanField(default=False)
    # True if segment is redundant and redundancy
    # currently broken
    lost_redundancy = BooleanField(default=False)
    # VLAN namespace demarcation
    # * False - share namespace with parent VLAN
    # * True - split own namespace
    vlan_border = BooleanField(default=True)
    # VLAN translation policy when marking border
    # (vlan_border=True)
    # Dynamically recalculated and placed to VLAN.translation_rule
    # and VLAN.parent
    vlan_translation = ListField(EmbeddedDocumentField(VLANTranslation))
    # Share allocation resources with another segments
    allocation_group = PlainReferenceField(AllocationGroup)
    # Provided L2 MTU
    l2_mtu = IntField(default=1504)
    # Administrative domains which have access to segment
    # Sum of all administrative domains
    adm_domains = ListField(IntField())
    # Collapse object's downlinks on network map
    # when count is above the threshold
    max_shown_downlinks = IntField(default=1000)
    # Limit objects on network map for reach "Too many objects" error
    max_objects = IntField(default=300)
    # Horizontal transit policy
    horizontal_transit_policy = StringField(
        choices=[("E", "Always Enable"), ("C", "Calculate"), ("D", "Disable"), ("P", "Profile")],
        default="P",
    )
    # Horizontal transit settings
    # i.e. Allow traffic flow not only from parent-to-childrens and
    # children-to-children, but parent-to-parent and parent-to-neighbors
    # Calculated automatically during topology research
    enable_horizontal_transit = BooleanField(default=False)
    # Objects, services and subscribers belonging to segment directly
    direct_objects = ListField(EmbeddedDocumentField(ObjectSummaryItem))
    direct_services = ListField(EmbeddedDocumentField(SummaryItem))
    direct_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Objects, services and subscribers belonging to all nested segments
    total_objects = ListField(EmbeddedDocumentField(ObjectSummaryItem))
    total_services = ListField(EmbeddedDocumentField(SummaryItem))
    total_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _border_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _vlan_domains_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _vlan_domains_mo_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DISCOVERY_JOB = "noc.services.discovery.jobs.segment.job.SegmentDiscoveryJob"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["NetworkSegment"]:
        return NetworkSegment.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["NetworkSegment"]:
        return NetworkSegment.objects.filter(bi_id=bi_id).first()

    @classmethod
    def _reset_caches(cls, id):
        try:
            del cls._id_cache[str(id),]  # Tuple
        except KeyError:
            pass

    @cachetools.cached(_path_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    def clean(self):
        if self.horizontal_transit_policy == "E":
            self.enable_horizontal_transit = True
        elif self.horizontal_transit_policy == "D":
            self.enable_horizontal_transit = False
        elif self.profile and self.horizontal_transit_policy == "P":
            if self.profile.horizontal_transit_policy == "E":
                self.enable_horizontal_transit = True
            elif self.profile.horizontal_transit_policy == "D":
                self.enable_horizontal_transit = False
        super().clean()

    @property
    def effective_settings(self):
        """
        Returns dict with effective settings
        """
        if hasattr(self, "_es"):
            return self._es
        # Build full parent stack
        sstack = [self.settings or {}]
        p = self.parent
        while p:
            sstack = [p.settings or {}] + sstack
            p = p.parent
        # Get effective settings
        es = {}
        for s in sstack:
            for k in s:
                v = s[k]
                if v:
                    # Override parent settings
                    es[k] = v
                elif k in es:
                    # Ignore parent settings
                    del es[k]
        self._es = es
        return es

    @property
    def managed_objects(self):
        from noc.sa.models.managedobject import ManagedObject

        siblings = self.get_siblings()
        if len(siblings) == 1:
            q = {"segment": str(siblings.pop().id)}
        else:
            q = {"segment__in": [str(s.id) for s in siblings]}
        return ManagedObject.objects.filter(**q)

    def get_siblings(self, seen=None):
        seen = seen or set()
        ss = {self}
        seen |= ss
        if self.sibling and self.sibling not in seen:
            ss |= self.sibling.get_siblings(seen)
        seen |= ss
        for s in NetworkSegment.objects.filter(sibling=self):
            ss |= s.get_siblings(seen)
        return ss

    def run_discovery(self):
        """
        Run discovery on whole segment
        """
        for o in self.managed_objects:
            if o.is_managed:
                o.run_discovery()

    @property
    def has_children(self):
        return bool(NetworkSegment.objects.filter(parent=self.id).only("id").first())

    def set_redundancy(self, status):
        """
        Change interface redundancy status
        :param status:
        :return:
        """
        siblings = list(self.get_siblings())
        filter = {"status": {"$ne": status}}
        if len(siblings) == 1:
            filter["_id"] = self.id
        else:
            filter["_id"] = {"$in": [s.id for s in siblings]}

        set_op = {"is_redundant": status}
        if not status:
            set_op["lost_redundancy"] = False
        NetworkSegment._get_collection().update_many(filter, {"$set": set_op})

    def set_lost_redundancy(self, status):
        NetworkSegment._get_collection().update_one(
            {"_id": self.id}, {"$set": {"lost_redundancy": bool(status)}}
        )

    def get_direct_summary(self):
        objects = {
            d["object_profile"]: d["count"]
            for d in self.managed_objects.values("object_profile")
            .annotate(count=Count("id"))
            .order_by("count")
        }
        # Direct services
        mo_ids = self.managed_objects.values_list("id", flat=True)
        services, subscribers = ServiceSummary.get_direct_summary(mo_ids)
        return services, subscribers, objects

    def get_summary(self):
        def to_list(v):
            return [{"profile": k, "summary": v[k]} for k in sorted(v)]

        def update_dict(d1, d2):
            for kk in d2:
                if kk in d1:
                    d1[kk] += d2[kk]
                else:
                    d1[kk] = d2[kk]

        services, subscribers, objects = self.get_direct_summary()
        r = {
            "direct_services": to_list(services),
            "direct_subscribers": to_list(subscribers),
            "direct_objects": to_list(objects),
        }
        # map(lambda x: update_dict(*x), zip([services, subscribers, objects], self.get_total_summary()))
        [
            update_dict(k, v)
            for k, v in zip([services, subscribers, objects], self.get_total_summary())
        ]
        r["total_services"] = to_list(services)
        r["total_subscribers"] = to_list(subscribers)
        r["total_objects"] = to_list(objects)
        return r

    @classmethod
    def update_summary(cls, network_segment):
        """
        Update summaries
        :return:
        """
        if not hasattr(network_segment, "id"):
            network_segment = NetworkSegment.get_by_id(network_segment)
        path = network_segment.get_path()
        # Update upwards
        path.reverse()
        for ns in sorted(
            NetworkSegment.objects.filter(id__in=path), key=lambda x: path.index(x.id)
        ):
            r = ns.get_summary()
            NetworkSegment._get_collection().update_one({"_id": ns.id}, {"$set": r}, upsert=True)

    def update_access(self):
        from noc.sa.models.administrativedomain import AdministrativeDomain

        # Get all own administrative domains
        adm_domains = set(
            d["administrative_domain"]
            for d in self.managed_objects.values("administrative_domain")
            .annotate(count=Count("id"))
            .order_by("count")
        )
        p = set()
        for a in adm_domains:
            a = AdministrativeDomain.get_by_id(a)
            p |= set(a.get_path())
        adm_domains |= p
        # Merge with children's administrative domains
        for s in NetworkSegment.objects.filter(parent=self.id).only("adm_domains"):
            adm_domains |= set(s.adm_domains or [])
        # Check for changes
        if set(self.adm_domains) != adm_domains:
            self.adm_domains = sorted(adm_domains)
            self.save()
            # Propagate to parents
            if self.parent:
                self.parent.update_access()

    def get_horizontal_transit_policy(self):
        if self.horizontal_transit_policy in ("E", "C"):
            return self.horizontal_transit_policy
        elif self.horizontal_transit_policy == "P" and self.profile:
            return self.profile.horizontal_transit_policy
        return "D"

    def get_effective_l2_domain(self) -> Optional["L2Domain"]:
        if self.l2_domain or not self.parent:
            return self.l2_domain
        return self.parent.get_effective_l2_domain()

    def get_management_vlan(self):
        """
        Returns Management VLAN for segment
        :return: vlan (integer) or None
        """
        if self.management_vlan_policy == "e":
            return self.management_vlan or None
        elif self.management_vlan_policy == "p":
            return self.profile.management_vlan or None
        return None

    def get_multicast_vlan(self):
        """
        Returns Multicast VLAN for segment
        :return: vlan (integer) or None
        """
        if self.multicast_vlan_policy == "e":
            return self.multicast_vlan or None
        elif self.multicast_vlan_policy == "p":
            return self.profile.multicast_vlan or None
        else:
            return None

    def get_nested_ids(self):
        """
        Return id of this and all nested segments
        :return:
        """
        # $graphLookup hits 100Mb memory limit. Do not use it
        seen = {self.id}
        wave = {self.id}
        max_level = 10
        coll = NetworkSegment._get_collection()
        for _ in range(max_level):
            # Get next wave
            wave = (
                set(d["_id"] for d in coll.find({"parent": {"$in": list(wave)}}, {"_id": 1})) - seen
            )
            if not wave:
                break
            seen |= wave
        return list(seen)

    def ensure_discovery_jobs(self):
        if self.profile and self.profile.discovery_interval > 0:
            Job.submit("scheduler", self.DISCOVERY_JOB, key=self.id, keep_ts=True)
        else:
            Job.remove("scheduler", self.DISCOVERY_JOB, key=self.id)

    def on_save(self):
        from noc.sa.models.managedobject import MANAGEDOBJECT_CACHE_VERSION

        if hasattr(self, "_changed_fields") and "profile" in self._changed_fields:
            self.ensure_discovery_jobs()
        if (
            hasattr(self, "_changed_fields")
            and self.vlan_border
            and "vlan_translation" in self._changed_fields
        ):
            from noc.vc.models.vlan import VLAN

            for vlan in VLAN.objects.filter(segment=self.id):
                vlan.refresh_translation()
        if hasattr(self, "_changed_fields") and "parent" in self._changed_fields:
            self.update_access()
            self.update_links()
            if self.parent:
                self.parent.update_links()
        # Clean cache
        cache.delete_many(
            [f"managedobject-id-{x}" for x in self.managed_objects.values_list("id", flat=True)],
            version=MANAGEDOBJECT_CACHE_VERSION,
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_border_cache"), lock=lambda _: id_lock)
    def get_border_segment(cls, segment):
        """
        Proceed up until vlan border
        :return:
        """
        current = segment
        while current:
            if current.vlan_border or not current.parent:
                return current
            current = current.parent

    @classmethod
    def iter_vlan_domain_segments(cls, segment):
        """
        Get all segments related to same VLAN domains
        :param segment:
        :return:
        """

        def iter_segments(ps):
            # Return segment
            yield ps
            # Iterate and recurse over all non vlan-border children
            for s in NetworkSegment.objects.filter(parent=ps.id):
                if s.vlan_border:
                    continue
                yield from iter_segments(s)

        # Get domain root
        root = cls.get_border_segment(segment)
        # Yield all children segments
        yield from iter_segments(root)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_vlan_domains_cache"), lock=lambda _: id_lock)
    def get_vlan_domain_segments(cls, segment):
        """
        Get list of all segments related to same VLAN domains
        :param segment:
        :return:
        """
        return list(cls.iter_vlan_domain_segments(segment))

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_vlan_domains_mo_cache"), lock=lambda _: id_lock)
    def get_vlan_domain_object_ids(cls, segment):
        """
        Get list of all managed object ids belonging to
        same VLAN domain
        :param segment:
        :return:
        """
        from noc.sa.models.managedobject import ManagedObject

        return ManagedObject.objects.filter(
            segment__in=[s.id for s in cls.get_vlan_domain_segments(segment)]
        ).values_list("id", flat=True)

    def iter_links(self):
        yield from Link.objects.filter(linked_segments__in=[self.id])

    def update_links(self):
        # @todo intersect link only
        for link in self.iter_links():
            link.save()

    def get_total_summary(self, ids=None, parent_id=None):
        """

        :param ids: Network segment ID list
        :param parent_id: Parent ID filter value
        :return:
        """
        services = {}
        subscribers = {}
        objects = {}
        pipeline = []
        # Exclude segment sibling set (sibling segments as one)
        match = {"sibling": None}
        if ids:
            # Filter by network segment
            match["_id"] = {"$in": ids}
        else:
            match["parent"] = parent_id or self.id
        if match:
            pipeline += [{"$match": match}]
        # Mark service and profile with type field
        pipeline += [
            {
                "$project": {
                    "_id": 0,
                    "service": {
                        "$map": {
                            "input": "$total_services",
                            "as": "svc",
                            "in": {
                                "type": "svc",
                                "profile": "$$svc.profile",
                                "summary": "$$svc.summary",
                            },
                        }
                    },
                    "subscriber": {
                        "$map": {
                            "input": "$total_subscribers",
                            "as": "sub",
                            "in": {
                                "type": "sub",
                                "profile": "$$sub.profile",
                                "summary": "$$sub.summary",
                            },
                        }
                    },
                    "object": {
                        "$map": {
                            "input": "$total_objects",
                            "as": "obj",
                            "in": {
                                "type": "obj",
                                "profile": "$$obj.profile",
                                "summary": "$$obj.summary",
                            },
                        }
                    },
                }
            },
            # Concatenate services and profiles
            {"$project": {"summary": {"$concatArrays": ["$service", "$subscriber", "$object"]}}},
            # Unwind *summary* array to independed records
            {"$unwind": "$summary"},
            # Group by (type, profile)
            {
                "$group": {
                    "_id": {"type": "$summary.type", "profile": "$summary.profile"},
                    "summary": {"$sum": "$summary.summary"},
                }
            },
        ]  # noqa
        try:
            for doc in NetworkSegment._get_collection().aggregate(pipeline):
                profile = doc["_id"]["profile"]
                if doc["_id"]["type"] == "svc":
                    services[profile] = services.get(profile, 0) + doc["summary"]
                elif doc["_id"]["type"] == "sub":
                    subscribers[profile] = subscribers.get(profile, 0) + doc["summary"]
                elif doc["_id"]["type"] == "obj":
                    objects[profile] = objects.get(profile, 0) + doc["summary"]
        except OperationFailure:
            # for Mongo less 3.4
            pass
        return services, subscribers, objects

    def get_topology_node(self) -> TopologyNode:
        return TopologyNode(
            id=str(self.id),
            type="objectsegment",
            resource_id=str(self.id),
            title=self.name,
        )
