# ----------------------------------------------------------------------
# Message NoData Checker for collector services
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from collections import defaultdict
from time import perf_counter
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any

# NOC modules
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.loader import get_service
from noc.core.checkers.base import NODATA
from noc.core.mx import MessageType, MX_JOB_HANDLER

logger = logging.getLogger(__name__)
MAX_SEND_OBJECTS = 100


@dataclass
class DataSourceRecord:
    """Record in Storm Table"""

    __slots__ = (
        "collector",
        "data_ts",
        "last_ts",
        "raised_alarm",
        "register_message",
        "remote_system",
        "ttl",
    )
    data_ts: datetime.datetime
    last_ts: int
    ttl: int
    raised_alarm: bool
    register_message: bool
    collector: str
    remote_system: Optional[str]
    # partial check: List[Tuple[ts, code]]

    def is_no_data(self, ts: Optional[int] = None) -> bool:
        """Check item last received data over ttl"""
        ts = ts or int(perf_counter())
        return (ts - self.last_ts) > self.ttl

    def update_data(self, ts: datetime.datetime):
        """Update data ts"""
        self.data_ts = ts
        self.last_ts = int(perf_counter())

    def is_register(self) -> bool:
        """Check has register update message. Add Update_ttl"""
        return self.register_message

    def is_out_ttl(self, ts: int) -> bool:
        return (ts - self.last_ts) > (self.ttl + 3600)

    def get_check_status_msg(self, status: bool) -> Dict[str, Any]:
        """"""
        r = {
            "check": NODATA,
            "status": status,
            "args": {"collector": self.collector},
        }
        if self.remote_system:
            r["remote_system"] = self.remote_system
        if not status:
            r["error"] = {"code": "1", "message": f"Not received data between {self.ttl}"}
        return r


class NoDataChecker(object):
    """
    Control input data from source, and set flag in no updated data on TTL
    Attributes:
        nodata_record_ttl: Time when not data allowed
        nodata_round_duration: No Data check handler execute interval
        alarm_class: No Data Alarm Class
        collector: collector name
    """

    def __init__(
        self,
        nodata_record_ttl: Optional[int] = 3600,
        nodata_round_duration: Optional[int] = 60,
        alarm_class: Optional[str] = None,
        collector: Optional[str] = None,
    ):
        self.nodata_round_duration = nodata_round_duration
        self.nodata_record_ttl = nodata_record_ttl
        self.alarm_class = alarm_class
        self.service = get_service()
        self.collector = collector or self.service.name
        self.source_table: Dict[Tuple[str, str, str], DataSourceRecord] = {}

    def initialize(self):
        """
        Launches periodical callback of verification round
        """
        pt = PeriodicCallback(self.ttl_round_handler, self.nodata_round_duration * 1000)
        pt.start()
        logger.info(
            "NoData Checker activated and now working with round duration %s seconds",
            self.nodata_round_duration,
        )

    def device_is_no_data(
        self,
        source_id: str,
        collector: Optional[str] = None,
        remote_system: Optional[str] = None,
    ) -> bool:
        return self.source_table[
            (source_id, collector or self.collector, remote_system or "")
        ].is_no_data()

    async def ttl_round_handler(self):
        """"""
        to_delete, no_data_count, messages = [], 0, {}
        ts = int(perf_counter())
        for key, item in self.source_table.items():
            no_data = item.is_no_data(ts)
            sid = key[0]
            if no_data and not item.is_register():
                # self.register_status_message(item, False)
                messages[sid] = item.get_check_status_msg(False)
                item.register_message = True
                no_data_count += 1
            elif not no_data and item.is_register():
                # self.register_status_message(item, True)
                messages[sid] = item.get_check_status_msg(True)
                item.register_message = False
            if no_data and item.is_out_ttl(ts):
                to_delete.append(key)
            # Update TTL
            if item.ttl != self.nodata_record_ttl:
                item.ttl = self.nodata_record_ttl
            if len(messages) > MAX_SEND_OBJECTS:
                await self.register_status_messages(messages)
                messages = {}
        if messages:
            await self.register_status_messages(messages)
        for key in to_delete:
            del self.source_table[key]
        logger.info("End of NoData Check round: found %d no data devices", no_data_count)
        logger.info("Data Sources: %s", len(self.source_table))

    async def register_status_messages(self, records: Dict[str, Dict[str, Any]]):
        """Register status message"""
        logger.debug("Register status message on: %s", records)
        # id: str
        # target_type: Literal["managed_object", "service"] = "managed_object"
        # statuses: List[CheckResultItem]
        r = defaultdict(list)
        for key, result in records.items():
            k = f"sa.ManagedObject:bi_id:{key}"
            r[k].append(result)
        await self.service.send_message(
            {"results": r},
            MessageType.JOB,
            headers={MX_JOB_HANDLER: b"noc.core.diagnostic.hub.update_diagnostic_checks"},
        )

    def register_data(
        self,
        source_id: str,
        ts: datetime.datetime,
        collector: Optional[str] = None,
        remote_system: Optional[str] = None,
    ):
        """
        Register received data from source
        Args:
            source_id: Source Identifier
            ts: Timestamp when received data
            collector: Data collector name (if not set - use default)
            remote_system: Remote System from received
        """
        # RemoteSystem
        collector = collector or self.collector
        # source id from different source. Check Received Data from Another system
        key = (source_id, collector, remote_system or "")
        if key in self.source_table:
            self.source_table[key].update_data(ts)
            # Register New
            return
        self.source_table[key] = DataSourceRecord(
            last_ts=int(perf_counter()),
            data_ts=ts,
            ttl=self.nodata_record_ttl,
            raised_alarm=False,
            register_message=True,  # Set True to Registered
            collector=collector,
            remote_system=remote_system,
        )
        # Send update checker
