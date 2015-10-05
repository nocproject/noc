# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmJob base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.multiintervaljob import MultiIntervalJob
from noc.fm.models import ActiveAlarm


class AlarmJob(MultiIntervalJob):
    model = ActiveAlarm  # self.object is an ActiveAlarm instance

    def __init__(self, *args, **kwargs):
        super(AlarmJob, self).__init__(*args, **kwargs)
        self.cleared = False

    def get_managed_object(self):
        return self.object.managed_object

    def clear_alarm(self, message):
        self.info("Clearing alarm %s: %s" % (self.object.id, message))
        self.object.clear_alarm(message)
        self.cleared = True

    def get_schedule(self, status):
        if self.cleared:
            return None  # Remove schedule
        else:
            return super(AlarmJob, self).get_schedule(status)

    @classmethod
    def get_job_config(cls, alarm, cfg):
        """
        Returns Job's *submit* arguments.
        :param alarm: ActiveAlarm instance
        :param cfg: dict of config
        """
        return {
            "interval": [(None, cfg["interval"])]
        }

    def can_run(self):
        if self.map_task:
            mo = self.get_managed_object()
            if not mo.is_managed:
                self.logger.debug("Object is not managed")
                return False
            if not mo.get_status():
                self.logger.debug("Object is down")
                return False
        return True
