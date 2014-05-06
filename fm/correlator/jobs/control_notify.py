# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator job:
## Notify alarm close after the control time
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job
from noc.fm.models.archivedalarm import ArchivedAlarm


class ControlNotifyJob(Job):
    name = "control_notify"
    model = ArchivedAlarm

    def handler(self, *args, **kwargs):
        if not self.object.root:
            self.object.managed_object.event(
                self.object.managed_object.EV_ALARM_CLEARED,
                {
                    "alarm": self.object,
                    "subject": self.object.get_translated_subject("en"),
                    "body": self.object.get_translated_body("en"),
                    "symptoms": self.object.get_translated_symptoms("en"),
                    "recommended_actions": self.object.get_translated_recommended_actions("en"),
                    "probable_causes": self.object.get_translated_probable_causes("en")
                }
            )
        return True
