# ----------------------------------------------------------------------
# Message storm protection for collectors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
import logging
from typing import Dict

# NOC modules
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.loader import get_service

logger = logging.getLogger(__name__)


@dataclass
class StormRecord:
    """Record in storm table"""

    messages_count: int = 0
    talkative: bool = False
    ttl: int = 0


class StormProtection(object):
    """Message storm protection functionality"""

    storm_table: Dict[str, StormRecord] = {}

    def __init__(self):
        self.storm_round_duration = None
        self.storm_threshold_reduction = None
        self.storm_record_ttl = None
        self.service = None

    def initialize(self, storm_round_duration, storm_threshold_reduction, storm_record_ttl):
        self.storm_round_duration = storm_round_duration
        self.storm_threshold_reduction = storm_threshold_reduction
        self.storm_record_ttl = storm_record_ttl
        self.service = get_service()
        pt = PeriodicCallback(self.storm_round, self.storm_round_duration * 1000)
        pt.start()

    async def storm_round(self):
        to_delete = []
        for ip in self.storm_table:
            record = self.storm_table[ip]
            logger.debug(f"storm_round: record.messages_count: {record.messages_count}")
            cfg = self.service.address_configs[ip]
            # set new value to talkative flag
            if record.messages_count > cfg.storm_threshold:
                record.talkative = True
            if record.messages_count < round(cfg.storm_threshold * self.storm_threshold_reduction):
                record.talkative = False
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


storm_protection = StormProtection()
