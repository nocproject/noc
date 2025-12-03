# ----------------------------------------------------------------------
# ETL Sync Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from time import perf_counter
from collections import defaultdict
from typing import List, Dict

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.core.mx import send_message, MessageType
from noc.core.etl.remotesystem.base import StepResult
from noc.core.service.loader import get_service
from noc.core.jsonutils import iter_chunks
from noc.core.models.sensorprotos import SensorProtocol
from noc.main.models.remotesystem import RemoteSystem
from noc.inv.models.sensor import Sensor
from noc.inv.models.sensorprofile import SensorProfile
from noc.config import config

NS = 1_000_000_000


class RemoteSystemJob(PeriodicJob):
    model = RemoteSystem

    def handler(self, **kwargs):
        """Processed Sync"""

    def process_detail(self, details: List[StepResult], duration: float = 0):
        """Process details"""
        # Send report
        summary = defaultdict(dict)
        for d in details:
            if not d.has_changed:
                continue
            summary[d.loader].update(d.summary)
        if self.object.sync_notification != "A":
            return
        send_message(
            {
                "remote_system": {"name": self.object.name, "id": str(self.object.id)},
                "ts": datetime.datetime.now().replace(microsecond=0).isoformat(),
                "duration": duration,
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


class ETLSyncJob(RemoteSystemJob):
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
        r = self.object.extract(quiet=True, exclude_fmevent=True)
        self.logger.info("[extract] Duration")
        if not r:
            self.register_error("extract", error=self.object.extract_error)
            return
        details = r
        r = self.object.check()
        if not r:
            self.register_error("check", error="Error when checking records")
            return
        details += r[1]
        # Report self.object.di
        r = self.object.load(quiet=True, exclude_fmevent=True)
        if not r:
            self.register_error("load", error=self.object.load_error)
            return
        details += r
        self.process_detail(details, duration=perf_counter() - t0)


class ETLEventSyncJob(RemoteSystemJob):
    model = RemoteSystem

    def handler(self, **kwargs):
        """Processed FM Event"""
        r = self.object.extract(extractors=["fmevent"], quiet=True)
        self.logger.info("[extract] Duration")
        if not r:
            self.register_error("extract", error=self.object.extract_error)
            return
        details = r
        r = self.object.check(extractors=["fmevent"])
        if not r:
            self.register_error("check", error="Error when checking records")
            return
        details += r[1]
        # Report self.object.di
        r = self.object.load(extractors=["fmevent"], quiet=True)
        if not r:
            self.register_error("load", error=self.object.load_error)
            return
        details += r

    def can_run(self):
        return self.object.enable_sync and self.object.event_sync_interval

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return self.object.event_sync_interval


class ETLMetricSyncJob(RemoteSystemJob):
    model = RemoteSystem

    def handler(self, **kwargs):
        """Processed Pull metrics on Remote System"""
        extractor = self.object.get_metric_extractor()
        if not extractor:
            self.logger.info("Metrics extractor not supported for RemoteSystem. Skipping..")
            return
        now = datetime.datetime.now().replace(microsecond=0)
        profiles = SensorProfile.objects.filter(enable_collect=True).scalar("id")
        if not profiles:
            RemoteSystem.objects.filter(id=self.object.id).update(
                last_extract_metrics=now,
            )
            return
        svc = get_service()
        metrics_svc_slots = svc.get_slot_limits("metrics")
        if not metrics_svc_slots:
            self.logger.warning("No active Metrics service. Skipping...")
            return
        self.logger.info("Run extract metrics")
        parts = defaultdict(list)
        extract_sensors: Dict[str, Sensor] = {}
        sensors, values = 0, 0
        for s in Sensor.objects.filter(
            remote_system=self.object,
            protocol=SensorProtocol.REMOTE_PULL,
            profile__in=profiles,
        ):
            extract_sensors[s.local_id] = s
        try:
            for local_id, metric_name, series in extractor.iter_metrics(
                item_ids=list(extract_sensors),
                end_ts=now,
            ):
                s = extract_sensors.get(local_id)
                if not s:
                    continue
                sensors += 1
                for ts, value in series:
                    s.set_value(value, ts, bulk=parts, shards=metrics_svc_slots)
                    values += 1
        except Exception as e:
            self.logger.error("Error when extract metrics from Remote System: %s", str(e))
        if not parts:
            return
        self.logger.info("Send sensors: %s, Values: %s", sensors, values)
        RemoteSystem.objects.filter(id=self.object.id).update(
            last_extract_metrics=now,
            last_successful_extract_metrics=now,
        )
        for partition, items in parts.items():
            for d in iter_chunks(
                items,
                max_size=config.msgstream.max_message_size,
            ):
                svc.publish(
                    value=d,
                    stream="metrics",
                    partition=partition,  # self.object.bi_id % metrics_svc_slots,
                    headers={},
                )

    def can_run(self):
        return self.object.enable_metrics and self.object.remote_collectors_policy == "D"

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return 120
