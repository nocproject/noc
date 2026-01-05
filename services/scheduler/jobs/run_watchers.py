# ----------------------------------------------------------------------
# Watcher Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.models import get_model
from noc.core.scheduler.periodicjob import PeriodicJob

WAIT_DEFAULT_INTERVAL_SEC = 180
MIN_NEXT_SHIFT_SEC = 30


class RunWatchersJob(PeriodicJob):
    def handler(self, **kwargs):
        self.logger.info("Run watcher for model: %s, %s", kwargs, self.attrs[self.ATTR_KEY])
        model = get_model(self.attrs[self.ATTR_KEY])
        now = datetime.datetime.now().replace(microsecond=0)
        for svc in model.objects.filter(watcher_wait_ts__lte=now):
            for w in svc.touch_watch():
                a = w.get_action()
                self.logger.debug("[%s] Touch Watch: %s / Action: %s", svc, w, a)
                if not a or not a.is_supported(svc):
                    continue
                # Send to Worker
                a.run_action(svc, w.key, w.args)
                if w.once:
                    svc.stop_watch(w.effect, w.key, remote_system=w.remote_system)
                # Clean After
            # Bulk ?
        # Clean cache

    def can_run(self):
        return True

    def get_next_timestamp(self, interval, offset=0.0, ts=None):
        """
        Returns next repeat interval
        """
        model = get_model(self.attrs[self.ATTR_KEY])

        now = datetime.datetime.now().replace(microsecond=0)
        next_ts = model.get_min_wait_ts()
        if not next_ts:
            next_ts = now + datetime.timedelta(seconds=WAIT_DEFAULT_INTERVAL_SEC)
        elif next_ts <= now:
            next_ts = now + datetime.timedelta(seconds=MIN_NEXT_SHIFT_SEC)
        return next_ts
