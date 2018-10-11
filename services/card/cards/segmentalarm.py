# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Segment Alarm card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
# NOC modules
from .base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import SummaryItem
from noc.inv.models.networksegment import NetworkSegment


class SegmentAlarmCard(BaseCard):
    name = "segmentalarm"
    default_template_name = "segmentalarm"
    model = NetworkSegment

    def get_data(self):
        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        def process_segment(r, segment):
            # Self alarms
            if segment.id in aseg:
                for a in aseg[segment.id]:
                    r["alarms"] += [{
                        "alarm_id": a.id,
                        "object": a.managed_object,
                        "alarm": a,
                        "severity": a.severity,
                        "timestamp": a.timestamp,
                        "duration": a.display_duration,
                        "escalation_tt": a.escalation_tt or "",
                        "summary": {
                            "subscriber": SummaryItem.items_to_dict(a.direct_subscribers),
                            "service": SummaryItem.items_to_dict(a.direct_services)
                        }
                    }]
            for ns in NetworkSegment.objects.filter(parent=segment.id):
                if ns.id not in seen_seg:
                    continue
                sr = {
                    "segment": ns,
                    "children": [],
                    "alarms": [],
                    "summary": {
                        "subscriber": {},
                        "service": {}
                    }
                }
                process_segment(sr, ns)
                r["children"] += [sr]

        def update_summary(r):
            services = r["summary"]["service"]
            subscribers = r["summary"]["subscriber"]
            for a in r["alarms"]:
                update_dict(services, a["summary"]["service"])
                update_dict(subscribers, a["summary"]["subscriber"])
            for c in r["children"]:
                update_summary(c)
                update_dict(services, c["summary"]["service"])
                update_dict(subscribers, c["summary"]["subscriber"])

        # Get alarms in all nested segments
        aseg = defaultdict(list)
        seen_seg = set()
        for a in ActiveAlarm.objects.filter(segment_path=self.object.id):
            seen_seg.update(a.segment_path)
            aseg[a.segment_path[-1]] += [a]
        #
        tree = {
            "segment": self.object,
            "children": [],
            "alarms": [],
            "summary": {
                "subscriber": {},
                "service": {}
            }
        }
        process_segment(tree, self.object)
        update_summary(tree)
        return {
            "tree": [tree]
        }
