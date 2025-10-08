# ---------------------------------------------------------------------
# Total Outage card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging

# NOC modules
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject
from .base import BaseCard

logger = logging.getLogger(__name__)


class OutageCard(BaseCard):
    name = "outage"
    default_template_name = "outage"
    card_css = ["/ui/card/css/outage.css"]

    def get_data(self):
        def update_summary(segment):
            """
            Calculate summary for segment and all nested segments
            """
            services = {}
            subscribers = {}
            # Calculate direct segments' coverage
            for o in segment["objects"].values():
                update_dict(services, o["services"])
                update_dict(subscribers, o["subscribers"])
                o["object"] = object_map[o["object"]]
            # Flatten objects
            segment["objects"] = sorted(segment["objects"].values(), key=lambda x: -x["weight"])
            # Calculate children's coverage
            for sid, s in segment["segments"].items():
                update_summary(s)
                update_dict(services, s["services"])
                update_dict(subscribers, s["subscribers"])
                s["segment"] = {"name": segment_map.get(sid, ""), "id": sid}
            segment["segments"] = sorted(segment["segments"].values(), key=lambda x: -x["weight"])
            segment["services"] = services
            segment["subscribers"] = subscribers
            segment["summary"] = {"service": services, "subscriber": subscribers}
            segment["weight"] = ServiceSummary.get_weight(segment["summary"])

        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        # Build tree
        tree = {"segment": None, "segments": {}, "objects": {}, "subscribers": {}, "services": {}}
        if self.current_user.is_superuser:
            qs = ActiveAlarm.objects.filter(root__exists=False)
        else:
            qs = ActiveAlarm.objects.filter(
                adm_path__in=self.get_user_domains(), root__exists=False
            )
        now = datetime.datetime.now()
        segments = set()
        objects = set()
        for alarm in qs.only(
            "total_services",
            "total_subscribers",
            "segment_path",
            "severity",
            "timestamp",
            "managed_object",
            "log",
        ).as_pymongo():
            if not alarm["total_services"] and not alarm["total_subscribers"]:
                continue
            ct = tree
            for sp_id in alarm["segment_path"]:
                if sp_id not in ct["segments"]:
                    ct["segments"][sp_id] = {
                        "segment": None,
                        "segments": {},
                        "objects": {},
                        "subscribers": {},
                        "services": {},
                    }
                ct = ct["segments"][sp_id]
                segments.add(sp_id)
            subscribers = {ss["profile"]: ss["summary"] for ss in alarm["total_subscribers"]}
            services = {ss["profile"]: ss["summary"] for ss in alarm["total_services"]}
            escalation_tt = None
            for ll in alarm["log"]:
                if ll.get("tt_id"):
                    escalation_tt = ll["tt_id"]
                    break
            ct["objects"][alarm["_id"]] = {
                "object": alarm["managed_object"],
                # "object": None,
                "alarm": alarm,
                "severity": alarm["severity"],
                "timestamp": alarm["timestamp"],
                "duration": now - alarm["timestamp"],
                "escalation_tt": escalation_tt or "",
                "subscribers": subscribers,
                "services": services,
                "summary": {"subscriber": subscribers, "service": services},
            }
            ct["objects"][alarm["_id"]]["weight"] = ServiceSummary.get_weight(
                ct["objects"][alarm["_id"]]["summary"]
            )
            objects.add(alarm["managed_object"])
        segment_map = dict(
            x
            for x in NetworkSegment.objects.filter(id__in=list(segments)).values_list("id", "name")
        )
        object_map = {
            x[0]: {"name": x[1], "container": x[2]}
            for x in ManagedObject.objects.filter(id__in=list(objects)).values_list(
                "id", "name", "container"
            )
        }
        # Calculate segment summaries
        update_summary(tree)
        # Calculate total summaries
        services = {}
        subscribers = {}
        for s in tree["segments"]:
            update_dict(services, s["summary"]["service"])
            update_dict(subscribers, s["summary"]["subscriber"])
        for o in tree["objects"]:
            update_dict(services, o["summary"]["service"])
            update_dict(subscribers, o["summary"]["subscriber"])
        tree["summary"] = {"subscriber": subscribers, "service": services}
        return tree
