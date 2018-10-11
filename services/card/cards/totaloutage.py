# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Total Outage card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import SummaryItem


class TotalOutageCard(BaseCard):
    name = "totaloutage"
    default_template_name = "totaloutage"

    def get_data(self):
        def update_dict(d1, d2):
            for k in d2:
                if k in d1:
                    d1[k] += d2[k]
                else:
                    d1[k] = d2[k]

        summary = {
            "subscriber": {},
            "service": {}
        }
        if self.current_user.is_superuser:
            qs = ActiveAlarm.objects.filter(root__exists=False)
        else:
            qs = ActiveAlarm.objects.filter(
                adm_path__in=self.get_user_domains(),
                root__exists=False
            )
        for a in qs.only("total_subscribers", "total_services"):
            update_dict(
                summary["subscriber"],
                SummaryItem.items_to_dict(a.total_subscribers or [])
            )
            update_dict(
                summary["service"],
                SummaryItem.items_to_dict(a.total_services or [])
            )
        return {
            "summary": summary,
            "is_clear": not summary["subscriber"] and not summary["service"]
        }
