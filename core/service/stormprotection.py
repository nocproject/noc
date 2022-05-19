# ----------------------------------------------------------------------
# Message storm protection for collectors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
import datetime
import logging
from typing import Dict

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.loader import get_service

logger = logging.getLogger(__name__)


@dataclass
class StormRecord:
    """Record in storm table"""

    messages_count: int = 0
    talkative: bool = False
    raised_alarm: bool = False
    ttl: int = 0


class StormProtection(object):
    """Message storm protection functionality"""

    def __init__(
        self, storm_round_duration, storm_threshold_reduction, storm_record_ttl, alarm_class
    ):
        self.storm_round_duration = storm_round_duration
        self.storm_threshold_reduction = storm_threshold_reduction
        self.storm_record_ttl = storm_record_ttl
        self.alarm_class = alarm_class
        self.service = get_service()
        self.storm_table: Dict[str, StormRecord] = {}

    def initialize(self):
        pt = PeriodicCallback(self.storm_round_handler, self.storm_round_duration * 1000)
        pt.start()

    async def storm_round_handler(self):
        to_delete = []
        for ip in self.storm_table:
            record = self.storm_table[ip]
            cfg = self.service.address_configs[ip]
            # set new value to talkative flag
            if record.messages_count > cfg.storm_threshold:
                record.talkative = True
            if record.messages_count < round(cfg.storm_threshold * self.storm_threshold_reduction):
                record.talkative = False
            if record.raised_alarm and not record.talkative:
                self._close_alarm(ip)
            # check time to live of record
            if record.messages_count == 0:
                record.ttl -= 1
            else:
                record.ttl = self.storm_record_ttl
            if record.ttl <= 0:
                to_delete.append(ip)
            else:
                # reset messages count
                record.messages_count = 0
        # delete old records
        for ip in to_delete:
            del self.storm_table[ip]

    def update_messages_counter(self, ip_address):
        if ip_address not in self.storm_table:
            self.storm_table[ip_address] = StormRecord()
            self.storm_table[ip_address].ttl = self.storm_record_ttl
        self.storm_table[ip_address].messages_count += 1

    def device_is_talkative(self, ip_address):
        return self.storm_table[ip_address].talkative

    def raise_alarm(self, ip_address):
        storm_record = self.storm_table[ip_address]
        if storm_record.raised_alarm:
            return
        cfg = self.service.address_configs[ip_address]
        msg = {
            "$op": "raise",
            "managed_object": cfg.id,
            "alarm_class": self.alarm_class,
        }
        self._publish_message(cfg, msg)
        storm_record.raised_alarm = True

    def _close_alarm(self, ip_address):
        cfg = self.service.address_configs[ip_address]
        msg = {"$op": "clear"}
        self._publish_message(cfg, msg)
        self.storm_table[ip_address].raised_alarm = False

    def _publish_message(self, cfg, msg):
        msg["timestamp"] = datetime.datetime.now().isoformat()
        msg["reference"] = f"{self.alarm_class}{cfg.id}"
        svc = self.service
        svc.publish(orjson.dumps(msg), stream=f"dispose.{config.pool}", partition=cfg.partition)
