# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ServiceSumamry Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
import logging
# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne, DeleteOne, InsertOne
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (IntField, ObjectIdField,
                                EmbeddedDocumentField, ListField)
# NOC modules
from noc.crm.models.subscriber import Subscriber
from noc.core.defer import call_later
from .serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile

logger = logging.getLogger(__name__)


class SummaryItem(EmbeddedDocument):
    profile = ObjectIdField()
    summary = IntField()

    @classmethod
    def items_to_dict(cls, items):
        """
        Convert a list of summary items to dict profile -> summary
        """
        return dict(
            (r.profile, r.summary)
            for r in items
        )

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
        return dict(
            (r.profile, r.summary)
            for r in items
        )

    @classmethod
    def dict_to_items(cls, d):
        """
        Convert a dict of profile -> summary to list of SummaryItem
        """
        return [ObjectSummaryItem(profile=k, summary=d[k]) for k in sorted(d)]


class ServiceSummary(Document):
    meta = {
        "collection": "noc.servicesummary",
        "indexes": [
            "managed_object",
            "interface"
        ]
    }
    managed_object = IntField()
    interface = ObjectIdField()
    service = ListField(EmbeddedDocumentField(SummaryItem))
    subscriber = ListField(EmbeddedDocumentField(SummaryItem))

    @classmethod
    def build_summary_for_object(cls, managed_object):
        from noc.inv.models.interface import Interface
        from noc.sa.models.service import Service

        def update_children(parent):
            for s in Service._get_collection().find({
                "parent": parent,
                "logical_status": "R"
            }, {
                "_id": 1,
                "subscriber": 1,
                "profile": 1
            }):
                subscribers.add(s["subscriber"])
                profiles[s["profile"]] += 1
                update_children(s["_id"])

        interfaces = dict(
            (x["_id"], x["service"])
            for x in Interface._get_collection().find({
                "managed_object": managed_object,
                "service": {
                    "$exists": True
                }
            }, {
                "_id": 1,
                "service": 1
            })
        )
        services = dict(
            (x["_id"], x)
            for x in Service._get_collection().find({
                "_id": {
                    "$in": list(interfaces.values())
                },
                "logical_status": "R"
            }, {
                "_id": 1,
                "subscriber": 1,
                "profile": 1
            })
        )

        ri = {}
        for i in interfaces:
            subscribers = set()
            profiles = defaultdict(int)
            service = services.get(interfaces[i])
            if not service:
                continue
            subscribers.add(service["subscriber"])
            profiles[service["profile"]] += 1
            update_children(interfaces[i])
            # Get subscriber profiles count
            ra = Subscriber._get_collection().aggregate([
                {
                    "$match": {
                        "_id": {
                            "$in": list(subscribers)
                        }
                    }
                }, {
                    "$group": {
                        "_id": "$profile",
                        "total": {
                            "$sum": 1
                        }
                    }
                }
            ])
            subscribers = dict((x["_id"], x["total"]) for x in ra)
            ri[i] = {
                "service": dict(profiles),
                "subscriber": subscribers
            }
        return ri

    @classmethod
    def refresh_object(cls, managed_object):
        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        call_later(
            "noc.sa.models.servicesummary.refresh_object",
            delay=20,
            managed_object=managed_object
        )

    @classmethod
    def _refresh_object(cls, managed_object):
        from noc.sa.models.managedobject import ManagedObject

        def to_dict(v):
            return dict(
                (r["profile"], r["summary"])
                for r in v
            )

        def to_list(v):
            return [{"profile": k, "summary": v[k]} for k in sorted(v)]

        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        collection = ServiceSummary._get_collection()
        bulk = []
        summary = cls.build_summary_for_object(managed_object)
        for s in ServiceSummary._get_collection().find({
            "managed_object": managed_object
        }, {
            "_id": 1,
            "interface": 1,
            "service": 1,
            "subscriber": 1
        }):
            ss = summary.get(s["interface"])
            if ss:
                service_profiles = to_dict(s["service"])
                subscriber_profiles = to_dict(s["subscriber"])
                if (service_profiles != ss["service"] or
                        subscriber_profiles != ss["subscriber"]):
                    bulk += [UpdateOne({
                        "_id": s["_id"]
                    }, {
                        "$set": {
                            "service": to_list(ss["service"]),
                            "subscriber": to_list(ss["subscriber"])
                        }
                    })]
                del summary[s["interface"]]
            else:
                bulk += [DeleteOne({
                    "_id": s["_id"]
                })]

        # add new
        for si, s in summary.items():
            # New interface
            bulk += [InsertOne({
                "managed_object": managed_object,
                "interface": si,
                "service": to_list(s["service"]),
                "subscriber": to_list(s["subscriber"])
            })]
        if bulk:
            logger.info("Commiting changes to database")
            try:
                r = collection.bulk_write(bulk, ordered=False)
                logger.info("Database has been synced")
                logger.info("Modify: %d, Deleted: %d", r.modified_count, r.deleted_count)
            except BulkWriteError as e:
                logger.error("Bulk write error: '%s'", e.details)
                logger.error("Stopping check")
        mo = ManagedObject.get_by_id(managed_object)
        mo.segment.update_summary()

    @classmethod
    def get_object_summary(cls, managed_object):
        def to_dict(v):
            return dict(
                (r["profile"], r["summary"])
                for r in v
            )

        if hasattr(managed_object, "id"):
            managed_object = managed_object.id
        r = {
            "service": {},
            "subscriber": {},
            "interface": {}
        }
        for ss in ServiceSummary._get_collection().find({
            "managed_object": managed_object
        }, {
            "interface": 1,
            "service": 1,
            "subscriber": 1
        }):
            ds = to_dict(ss["service"])
            if ss.get("interface"):
                r["interface"][ss["interface"]] = {
                    "service": ds
                }
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
    def get_weight(cls, summary):
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
        return w

    @classmethod
    def get_severity(cls, summary):
        """
        Convert result of *get_object_summary* to alarm severity
        """
        from noc.fm.models.alarmseverity import AlarmSeverity

        return AlarmSeverity.severity_for_weight(
            cls.get_weight(summary)
        )


def refresh_object(managed_object):
    ServiceSummary._refresh_object(managed_object)
