# ----------------------------------------------------------------------
# ETL Sync Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from time import perf_counter
from collections import defaultdict

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.main.models.remotesystem import RemoteSystem
from noc.core.mx import send_message, MessageType


class ETLSyncJob(PeriodicJob):
    model = RemoteSystem

    # catch lock, run, processed error
    # Add Lock to model
    def handler(self, **kwargs):
        # Check run, if node changed and not archived, need manual reset
        # if self.object.last_successful_load and not self.object.check_last_state():
        #     self.object.set_error(
        #         "pre_check",
        #         error="Not detect Last load state",
        #         recommended_actions="Check Last load state on scheduler node, if not checked - ",
        #     )
        #     return
        t0 = perf_counter()
        r = self.object.extract(quiet=True)
        self.logger.info("[extract] Duration")
        if not r:
            self.register_error("extract", error=self.object.extract_error)
            return
        details = r
        _, r = self.object.check()
        if not r:
            self.register_error("check", error="Error when checking records")
            return
        details += r
        # Report self.object.di
        r = self.object.load(quiet=True)
        if not r:
            self.register_error("load", error=self.object.load_error)
            return
        details += r
        # Send report
        summary = defaultdict(dict)
        for d in details:
            summary[d.loader].update(d.summary)
        if self.object.sync_notification != "A":
            return
        send_message(
            {
                "remote_system": {"name": self.object.name, "id": str(self.object.id)},
                "ts": datetime.datetime.now().replace(microsecond=0).isoformat(),
                "duration": perf_counter() - t0,
                "run_next": "",
                "details": details,
                "summary": summary,
            },
            message_type=MessageType.ETL_SYNC_REPORT,
            headers=self.object.get_mx_message_headers(),
        )

    def register_error(self, step, error):
        if self.object.sync_notification != "D":
            self.object.register_error(
                step,
                error=str(error),
                recommended_actions=f"Manually run './noc etl {step} <RS>' on extractor node and fix errors",
            )

    def can_run(self):
        return self.object.enable_sync and self.object.sync_interval

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return self.object.sync_interval
