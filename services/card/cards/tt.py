# ---------------------------------------------------------------------
# TT card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from .base import BaseCard
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.servicesummary import SummaryItem


class TTCard(BaseCard):
    name = "tt"
    default_template_name = "tt"

    def dereference(self, id):
        if ":" not in id:
            return None
        tts_name, tt_id = id.split(":", 1)
        tts = TTSystem.get_by_name(tts_name)
        if not tts:
            return None
        try:
            tts = tts.get_system()
            tt = tts.get_tt(tt_id)
        except NotImplementedError:
            # TTSystem does not support TT preview, redirect to alarm
            return self.redirect_to_alarm(id)
        if tt:
            tt["tt_system_name"] = tts_name
            tt["full_id"] = id
            return tt
        else:
            return None

    def get_data(self):
        r = self.object.copy()
        if r["resolved"]:
            r["duration"] = r["close_ts"] - r["open_ts"]
        else:
            r["duration"] = datetime.datetime.now() - r["open_ts"]
        r["alarms"] = []
        now = datetime.datetime.now()
        for ac in (ActiveAlarm, ArchivedAlarm):
            a = ac.objects.get_by_tt_id(r["full_id"])
            if a.status == "C":
                duration = a.clear_timestamp - a.timestamp
            else:
                duration = now - a.timestamp
            r["alarms"] += [
                {
                    "alarm": a,
                    "id": a.id,
                    "timestamp": a.timestamp,
                    "duration": duration,
                    "subject": a.subject,
                    "summary": {
                        "subscriber": SummaryItem.items_to_dict(a.total_subscribers),
                        "service": SummaryItem.items_to_dict(a.total_services),
                    },
                }
            ]
        return r

    def redirect_to_alarm(self, tt_id):
        """
        Find first alarm relative to URL
        :param tt_id:
        :return:
        """
        a = ActiveAlarm.objects.filter(escalation_tt=tt_id).order_by("timestamp").only("id").first()
        if not a:
            a = (
                ArchivedAlarm.objects.filter(escalation_tt=tt_id)
                .order_by("timestamp")
                .only("id")
                .first()
            )
        if not a:
            return
        self.redirect("/api/card/view/alarm/%s/" % a.id)
