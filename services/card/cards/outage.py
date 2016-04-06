# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Total Outage card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
## NOC modules
from base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import SummaryItem
import cachetools


class OutageCard(BaseCard):
    default_template_name = "outage"

    def get_data(self):
        def get_segment_path(segment):
            if segment.parent:
                return segment_path[segment.parent] + [segment]
            else:
                return [segment]

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
            # Flatten objects
            segment["objects"] = sorted(
                segment["objects"].values(),
                key=lambda x: -x["duration"]
            )
            # Calculate children's coverage
            for s in segment["segments"].values():
                update_summary(s)
                update_dict(services, s["services"])
                update_dict(subscribers, s["subscribers"])
            segment["segments"] = sorted(
                segment["segments"].values(),
                key=lambda x: x["segment"].name
            )
            segment["services"] = services
            segment["subscribers"] = subscribers
            segment["summary"] = {
                "service": services,
                "subscriber": subscribers
            }

        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        segment_path = cachetools.LRUCache(maxsize=10000,
                                           missing=get_segment_path)
        # Build tree
        tree = {
            "segment": None,
            "segments": {},
            "objects": {},
            "subscribers": {},
            "services": {}
        }
        now = datetime.datetime.now()
        for alarm in ActiveAlarm.objects.filter(root__exists=False):
            if not alarm.total_services and not alarm.total_subscribers:
                continue
            ct = tree
            for sp in segment_path[alarm.managed_object.segment]:
                if sp.id not in ct["segments"]:
                    ct["segments"][sp.id] = {
                        "segment": sp,
                        "segments": {},
                        "objects": {},
                        "subscribers": {},
                        "services": {}
                    }
                ct = ct["segments"][sp.id]
            subscribers = SummaryItem.items_to_dict(alarm.total_subscribers)
            services = SummaryItem.items_to_dict(alarm.total_services)
            ct["objects"][alarm.id] = {
                "object": alarm.managed_object,
                "alarm": alarm,
                "severity": alarm.severity,
                "timestamp": alarm.timestamp,
                "duration": now - alarm.timestamp,
                "escalation_tt": alarm.escalation_tt,
                "subscribers": subscribers,
                "services": services,
                "summary": {
                    "subscriber": subscribers,
                    "service": services
                }
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
        tree["summary"] = {
            "subscriber": subscribers,
            "service": services
        }
        return tree
