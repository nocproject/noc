# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Network Segment
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
import cachetools
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DictField, ReferenceField,
                                ListField, BooleanField, IntField,
                                EmbeddedDocumentField, LongField)
from mongoengine.errors import ValidationError
from django.db.models.aggregates import Count
# NOC modules
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.defer import call_later
from noc.core.bi.decorator import bi_sync
from .networksegmentprofile import NetworkSegmentProfile
from .allocationgroup import AllocationGroup
from .link import Link
from noc.core.scheduler.job import Job
from noc.vc.models.vcfilter import VCFilter

id_lock = Lock()


class VLANTranslation(EmbeddedDocument):
    filter = ForeignKeyField(VCFilter)
    rule = StringField(choices=[
        # Rewrite tag to parent vlan's
        ("map", "map"),
        # Append parent tag as S-VLAN
        ("push", "push")
    ], default="push")
    parent_vlan = PlainReferenceField("vc.VLAN")


@bi_sync
@on_delete_check(check=[
    ("sa.ManagedObject", "segment"),
    ("inv.NetworkSegment", "parent")
])
@on_save
class NetworkSegment(Document):
    meta = {
        "collection": "noc.networksegments",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "sibling", "adm_domains"]
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
        choices=[
            ("d", "Disable"),
            ("p", "Profile"),
            ("e", "Enable")
        ],
        default="p"
    )
    management_vlan = IntField(required=False, min_value=1, max_value=4095)
    # MVR VLAN processing order
    # * d - disable multicast vlan
    # * e - enable multicast vlan and get from multicast_vlan field
    # * p - use profile settings
    multicast_vlan_policy = StringField(
        choices=[
            ("d", "Disable"),
            ("p", "Profile"),
            ("e", "Enable")
        ],
        default="p"
    )
    multicast_vlan = IntField(required=False, min_value=1, max_value=4095)

    settings = DictField(default=lambda: {}.copy())
    tags = ListField(StringField())
    # Selectors for fake segments
    # Transition only, should not be used
    selector = ForeignKeyField(ManagedObjectSelector)
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
    # Horizontal transit policy
    horizontal_transit_policy = StringField(
        choices=[
            ("E", "Always Enable"),
            ("C", "Calculate"),
            ("D", "Disable"),
            ("P", "Profile")
        ], default="P"
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
    _path_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _border_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _vlan_domains_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _vlan_domains_mo_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DISCOVERY_JOB = "noc.services.discovery.jobs.segment.job.SegmentDiscoveryJob"

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return NetworkSegment.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return NetworkSegment.objects.filter(bi_id=id).first()

    @cachetools.cachedmethod(operator.attrgetter("_path_cache"), lock=lambda _: id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        else:
            return [self.id]

    def clean(self):
        if self.id and "parent" in self._changed_fields and self.has_loop:
            raise ValidationError("Creating segments loop")
        if self.horizontal_transit_policy == "E":
            self.enable_horizontal_transit = True
        elif self.horizontal_transit_policy == "D":
            self.enable_horizontal_transit = False
        elif self.profile and self.horizontal_transit_policy == "P":
            if self.profile.horizontal_transit_policy == "E":
                self.enable_horizontal_transit = True
            elif self.profile.horizontal_transit_policy == "D":
                self.enable_horizontal_transit = False
        super(NetworkSegment, self).clean()

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
    def has_loop(self):
        """
        Check if object creates loop
        """
        if not self.id:
            return False
        p = self.parent
        while p:
            if p.id == self.id:
                return True
            p = p.parent
        return False

    @property
    def managed_objects(self):
        from noc.sa.models.managedobject import ManagedObject

        if self.selector:
            return self.selector.managed_objects
        else:
            siblings = self.get_siblings()
            if len(siblings) == 1:
                q = {"segment": str(siblings.pop().id)}
            else:
                q = {"segment__in": [str(s.id) for s in siblings]}
            return ManagedObject.objects.filter(**q)

    def get_siblings(self, seen=None):
        seen = seen or set()
        ss = set([self])
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
        return bool(
            NetworkSegment.objects.filter(
                parent=self.id).only("id").first()
        )

    def set_redundancy(self, status):
        """
        Change interface redundancy status
        :param status:
        :return:
        """
        siblings = list(self.get_siblings())
        filter = {
            "status": {"$ne": status}
        }
        if len(siblings) == 1:
            filter["_id"] = self.id
        else:
            filter["_id"] = {
                "$in": [s.id for s in siblings]
            }

        set_op = {
            "is_redundant": status
        }
        if not status:
            set_op["lost_redundancy"] = False
        NetworkSegment._get_collection().update_many(
            filter, {
                "$set": set_op
            }
        )

    def set_lost_redundancy(self, status):
        NetworkSegment._get_collection().update({
            "_id": self.id
        }, {
            "$set": {
                "lost_redundancy": bool(status)
            }
        })

    def update_summary(self):
        """
        Update summaries
        :return:
        """
        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        objects = dict(
            (d["object_profile"], d["count"])
            for d in self.managed_objects.values(
                "object_profile"
            ).annotate(
                count=Count("id")
            ).order_by("count"))
        # Direct services
        mo_ids = self.managed_objects.values_list("id", flat=True)
        services, subscribers = ServiceSummary.get_direct_summary(mo_ids)
        self.direct_services = SummaryItem.dict_to_items(services)
        self.direct_subscribers = SummaryItem.dict_to_items(subscribers)
        self.direct_objects = ObjectSummaryItem.dict_to_items(objects)
        siblings = set()
        for ns in NetworkSegment.objects.filter(parent=self.id):
            if ns.id in siblings:
                continue
            update_dict(services, SummaryItem.items_to_dict(ns.total_services))
            update_dict(subscribers, SummaryItem.items_to_dict(ns.total_subscribers))
            update_dict(objects, ObjectSummaryItem.items_to_dict(ns.total_objects))
            siblings.add(ns.id)
            if ns.sibling:
                siblings.add(ns.sibling.id)
        self.total_services = SummaryItem.dict_to_items(services)
        self.total_subscribers = SummaryItem.dict_to_items(subscribers)
        self.total_objects = ObjectSummaryItem.dict_to_items(objects)
        self.save()
        # Update upwards
        ns = self.parent
        while ns:
            services = SummaryItem.items_to_dict(ns.direct_services)
            subscribers = SummaryItem.items_to_dict(ns.direct_subscribers)
            objects = ObjectSummaryItem.items_to_dict(ns.direct_objects)
            for nsc in NetworkSegment.objects.filter(parent=ns.id):
                update_dict(services, SummaryItem.items_to_dict(nsc.total_services))
                update_dict(subscribers, SummaryItem.items_to_dict(nsc.total_subscribers))
                update_dict(objects, ObjectSummaryItem.items_to_dict(nsc.total_objects))
            ns.total_services = SummaryItem.dict_to_items(services)
            ns.total_subscribers = SummaryItem.dict_to_items(subscribers)
            ns.total_objects = ObjectSummaryItem.dict_to_items(objects)
            ns.save()
            ns = ns.parent

    def update_access(self):
        from noc.sa.models.administrativedomain import AdministrativeDomain
        # Get all own administrative domains
        adm_domains = set(
            d["administrative_domain"]
            for d in self.managed_objects.values(
                "administrative_domain"
            ).annotate(
                count=Count("id")
            ).order_by("count")
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

    def update_uplinks(self):
        call_later(
            "noc.core.topology.segment.update_uplinks",
            60,
            segment_id=self.id
        )

    def get_horizontal_transit_policy(self):
        if self.horizontal_transit_policy in ("E", "C"):
            return self.horizontal_transit_policy
        elif self.horizontal_transit_policy == "P" and self.profile:
            return self.profile.horizontal_transit_policy
        else:
            return "D"

    def get_management_vlan(self):
        """
        Returns Management VLAN for segment
        :return: vlan (integer) or None
        """
        if self.management_vlan_policy == "e":
            return self.management_vlan or None
        elif self.management_vlan_policy == "p":
            return self.profile.management_vlan or None
        else:
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
        r = [self.id]
        r += [
            d["_id"] for d in
            NetworkSegment._get_collection().aggregate([
                {
                    "$match": {
                        "_id": self.id
                    }
                },
                {
                    "$graphLookup": {
                        "from": "noc.networksegments",
                        "startWith": "$_id",
                        "connectFromField": "_id",
                        "connectToField": "parent",
                        "as": "nested",
                        "maxDepth": 10
                    }
                },
                {
                    "$unwind": {
                        "path": "$nested"
                    }
                },
                {
                    "$project": {
                        "_id": "$nested._id"
                    }
                }
            ])]
        return r

    def ensure_discovery_jobs(self):
        if self.profile and self.profile.discovery_interval > 0:
            Job.submit(
                "scheduler",
                self.DISCOVERY_JOB,
                key=self.id,
                keep_ts=True
            )
        else:
            Job.remove(
                "scheduler",
                self.DISCOVERY_JOB,
                key=self.id
            )

    def on_save(self):
        if hasattr(self, "_changed_fields") and "profile" in self._changed_fields:
            self.ensure_discovery_jobs()
        if hasattr(self, "_changed_fields") and self.vlan_border and "vlan_translation" in self._changed_fields:
            from noc.vc.models.vlan import VLAN
            for vlan in VLAN.objects.filter(segment=self.id):
                vlan.refresh_translation()
        if hasattr(self, "_changed_fields") and "parent" in self._changed_fields:
            self.update_access()
            self.update_links()
            if self.parent:
                self.parent.update_links()

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
                for cs in iter_segments(s):
                    yield cs

        # Get domain root
        root = cls.get_border_segment(segment)
        # Yield all children segments
        for rs in iter_segments(root):
            yield rs

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
        for link in Link.objects.filter(linked_segments__in=[self.id]):
            yield link

    def update_links(self):
        # @todo intersect link only
        for link in self.iter_links():
            link.save()
