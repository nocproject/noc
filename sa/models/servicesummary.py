# ---------------------------------------------------------------------
# ServiceSumamry Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict
from collections import defaultdict
import logging

# Third-party modules
from pymongo.errors import BulkWriteError, OperationFailure
from pymongo import UpdateOne, DeleteOne, InsertOne
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import IntField, ObjectIdField, EmbeddedDocumentField, ListField

# NOC modules
from noc.crm.models.subscriber import Subscriber
from noc.core.defer import call_later
from .serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile

logger = logging.getLogger(__name__)


class SummaryItem(EmbeddedDocument):
    profile = ObjectIdField()
    summary = IntField()

    @classmethod
    def items_to_dict(cls, items):
        """
        Convert a list of summary items to dict profile -> summary
        """
        return {r.profile: r.summary for r in items}

    @classmethod
    def dict_to_items(cls, d):
        """
        Convert a dict of profile -> summary to list of SummaryItem
        """
        return [SummaryItem(profile=k, summary=d[k]) for k in sorted(d)]


class ObjectSummaryItem(EmbeddedDocument):
    profile = IntField()
    summary = IntField()

    @classmethod
    def items_to_dict(cls, items):
        """
        Convert a list of summary items to dict profile -> summary
        """
        return {r.profile: r.summary for r in items}

    @classmethod
    def dict_to_items(cls, d):
        """
        Convert a dict of profile -> summary to list of SummaryItem
        """
        return [ObjectSummaryItem(profile=k, summary=d[k]) for k in sorted(d)]


class ServiceSummary(Document):
    meta = {
        "collection": "noc.servicesummary",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["managed_object", "interface"],
    }
    managed_object = IntField()
    interface = ObjectIdField()
    subinterface = ObjectIdField()
    service = ListField(EmbeddedDocumentField(SummaryItem))
    subscriber = ListField(EmbeddedDocumentField(SummaryItem))

    @classmethod
    def build_summary_for_object(cls, managed_object):
        """
        Build active services summary for managed object
        :param managed_object: Managed Object id
        :return: dict of interface id -> {service: ..., subscriber: ....}
            interface None means unbound or box-wise services
        """
        from noc.sa.models.service import Service
        from noc.wf.models.state import State
        from noc.sa.models.serviceinstance import ServiceInstance

        def iter_services(sd):
            yield sd
            for cs in Service._get_collection().find(
                {"parent": sd["_id"], "state": {"$in": productive_states}},
                {"_id": 1, "subscriber": 1, "profile": 1},
            ):
                yield from iter_services(cs)

        def add_dict(d1, d2):
            """
            Add all d2 values to d1
            :param d1:
            :param d2:
            :return:
            """
            for k in d2:
                d1[k] = d1.get(k, 0) + d2[k]

        # Productive states
        productive_states = list(State.objects.filter(is_productive=True).values_list("id"))
        # Iterate over object's services
        # And walk underlying tree
        ri = {}
        for si in ServiceInstance.objects.filter(managed_object=managed_object):
            # All subscribers for underlying tree
            subscribers = set()
            # profile_id -> count
            svc_profiles = defaultdict(int)
            for s in iter_services(
                {
                    "_id": si.service.id,
                    "profile": si.service.profile.id,
                    "subscriber": si.service.subscriber.id if si.service.subscriber else None,
                }
            ):
                if s["subscriber"]:
                    subscribers.add(s["subscriber"])
                svc_profiles[s["profile"]] += 1
            # Get subscriber profiles count
            ra = Subscriber._get_collection().aggregate(
                [
                    {"$match": {"_id": {"$in": list(subscribers)}}},
                    {"$group": {"_id": "$profile", "total": {"$sum": 1}}},
                ]
            )
            subscriber_profiles = {x["_id"]: x["total"] for x in ra}
            # Bind to interface
            # None for unbound services
            iface = si.interface
            if not iface:
                ri[None] = {
                    "service": dict(svc_profiles),  # defaultdict -> dict
                    "subscriber": subscriber_profiles,
                }
                continue
            if iface in ri:
                add_dict(ri[iface.id]["service"], svc_profiles)
                add_dict(ri[iface.id]["subscriber"], subscriber_profiles)
            else:
                ri[iface.id] = {
                    "service": dict(svc_profiles),  # defaultdict -> dict
                    "subscriber": subscriber_profiles,
                }
        return ri

    @classmethod
    def refresh_object(cls, managed_object):
        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        call_later(
            "noc.sa.models.servicesummary.refresh_object", delay=20, managed_object=managed_object
        )

    @classmethod
    def _refresh_object(cls, managed_object):
        from noc.sa.models.managedobject import ManagedObject
        from noc.inv.models.networksegment import NetworkSegment

        def to_dict(v):
            return {r["profile"]: r["summary"] for r in v}

        def to_list(v):
            return [{"profile": k, "summary": v[k]} for k in sorted(v)]

        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        coll = ServiceSummary._get_collection()
        bulk = []
        # Get existing summary
        old_summary = {
            x["interface"]: x
            for x in coll.find(
                {"managed_object": managed_object},
                {"_id": 1, "interface": 1, "service": 1, "subscriber": 1},
                comment="[servicesummary._refresh_object] Refresh summary of services for managed object",
            )
            if "interface" in x
        }
        # Get actual summary
        new_summary = ServiceSummary.build_summary_for_object(managed_object)
        # Merge summaries
        for iface in old_summary:
            if iface not in new_summary:
                # Stale, delete
                bulk += [DeleteOne({"_id": old_summary[iface]["_id"]})]
                continue
            oi = old_summary[iface]
            old_services = to_dict(oi["service"])
            old_subs = to_dict(oi["subscriber"])
            ni = new_summary[iface]
            if old_services != ni["service"] or old_subs != ni["subscriber"]:
                # Changed, update
                bulk += [
                    UpdateOne(
                        {"_id": oi["_id"]},
                        {
                            "$set": {
                                "service": to_list(ni["service"]),
                                "subscriber": to_list(ni["subscriber"]),
                            }
                        },
                    )
                ]
            # Mark as processed
            del new_summary[iface]
        # Process new items
        bulk += [
            InsertOne(
                {
                    "managed_object": managed_object,
                    "interface": iface,
                    "service": to_list(new_summary[iface]["service"]),
                    "subscriber": to_list(new_summary[iface]["subscriber"]),
                }
            )
            for iface in new_summary
        ]
        if bulk:
            logger.info("Committing changes to database")
            try:
                r = coll.bulk_write(bulk, ordered=False)
                logger.info("Database has been synced")
                logger.info("Modify: %d, Deleted: %d", r.modified_count, r.deleted_count)
            except BulkWriteError as e:
                logger.error("Bulk write error: '%s'", e.details)
                logger.error("Stopping check")
        mo = ManagedObject.get_by_id(managed_object)
        NetworkSegment.update_summary(mo.segment)

    @classmethod
    def get_object_summary(cls, managed_object):
        def to_dict(v):
            return {r["profile"]: r["summary"] for r in v}

        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        r = {"service": {}, "subscriber": {}, "interface": {}}
        for ss in ServiceSummary._get_collection().find(
            {"managed_object": managed_object},
            {"interface": 1, "service": 1, "subscriber": 1},
            comment="[servicesummary.get_object_summary] Getting summary of services for object",
        ):
            ds = to_dict(ss["service"])
            if ss.get("interface"):
                r["interface"][ss["interface"]] = {"service": ds}
            for k, v in ds.items():
                if k in r["service"]:
                    r["service"][k] += v
                else:
                    r["service"][k] = v
            ds = to_dict(ss["subscriber"])
            if ss.get("interface"):
                r["interface"][ss["interface"]]["subscriber"] = ds
            for k, v in ds.items():
                if k in r["subscriber"]:
                    r["subscriber"][k] += v
                else:
                    r["subscriber"][k] = v
        return r

    @classmethod
    def get_objects_summary(cls, managed_objects):
        def to_dict(v):
            return {r["profile"]: r["summary"] for r in v}

        kk = {}
        for ss in ServiceSummary._get_collection().find(
            {"managed_object": {"$in": [getattr(mo, "id", mo) for mo in managed_objects]}},
            {"managed_object": 1, "interface": 1, "service": 1, "subscriber": 1},
            comment="[servicesummary.get_objects_summary] Getting summary of services for objects list",
        ):
            r = {"service": {}, "subscriber": {}, "interface": {}}
            ds = to_dict(ss["service"])
            if ss.get("interface"):
                r["interface"][ss["interface"]] = {"service": ds}
            for k, v in ds.items():
                if k in r["service"]:
                    r["service"][k] += v
                else:
                    r["service"][k] = v
            ds = to_dict(ss["subscriber"])
            if ss.get("interface"):
                r["interface"][ss["interface"]]["subscriber"] = ds
            for k, v in ds.items():
                if k in r["subscriber"]:
                    r["subscriber"][k] += v
                else:
                    r["subscriber"][k] = v
            kk[ss["managed_object"]] = r
        return kk

    @classmethod
    def get_weight(cls, summary: Dict[str, Dict[str, int]]) -> int:
        """
        Convert result of *get_object_summary* to alarm weight
        """
        w = 0
        subscribers = summary.get("subscriber", {})
        for s in subscribers:
            sp = SubscriberProfile.get_by_id(s)
            if sp and sp.weight:
                w += sp.weight * subscribers[s]
        services = summary.get("service", {})
        for s in services:
            sp = ServiceProfile.get_by_id(s)
            if sp and sp.weight:
                w += sp.weight * services[s]
        objects = summary.get("object", {})
        for s in objects:
            sp = ManagedObjectProfile.get_by_id(s)
            if sp and sp.weight:
                w += sp.weight * objects[s]
        interfaces = summary.get("interface", {})
        for s in interfaces:
            sp = InterfaceProfile.get_by_id(s)
            if sp and sp.weight:
                w += sp.weight * interfaces[s]
        return w

    @classmethod
    def get_severity(cls, summary) -> int:
        """
        Convert result of *get_object_summary* to alarm severity
        """
        from noc.fm.models.alarmseverity import AlarmSeverity

        return AlarmSeverity.severity_for_weight(cls.get_weight(summary))

    @classmethod
    def get_direct_summary(cls, managed_objects, summary_all=False):
        """
        ! Method works on mongodb version 3.4 and greater
        Calculate direct services and profiles for a list of managed objects
        :param managed_objects: List of managed object instances or ids
        :param summary_all: Return summary for all services
        :return: tuple of service and subscriber dicts
        """
        services = {}
        subscribers = {}
        pipeline = []
        if not summary_all:
            # Filter managed objects
            pipeline += [
                {
                    "$match": {
                        "managed_object": {"$in": [getattr(mo, "id", mo) for mo in managed_objects]}
                    }
                }
            ]
        # Mark service and profile with type field
        pipeline += [
            {
                "$project": {
                    "_id": 0,
                    "service": {
                        "$map": {
                            "input": "$service",
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
                            "input": "$subscriber",
                            "as": "sub",
                            "in": {
                                "type": "sub",
                                "profile": "$$sub.profile",
                                "summary": "$$sub.summary",
                            },
                        }
                    },
                }
            },
            # Concatenate services and profiles
            {"$project": {"summary": {"$concatArrays": ["$service", "$subscriber"]}}},
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
            for doc in ServiceSummary._get_collection().aggregate(pipeline):
                profile = doc["_id"]["profile"]
                if doc["_id"]["type"] == "svc":
                    services[profile] = services.get(profile, 0) + doc["summary"]
                else:
                    subscribers[profile] = subscribers.get(profile, 0) + doc["summary"]
        except OperationFailure:
            # for Mongo less 3.4
            pass
        return services, subscribers


def refresh_object(managed_object):
    ServiceSummary._refresh_object(managed_object)
