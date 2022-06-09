# ----------------------------------------------------------------------
# Message Storm Protection for collector services
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
import datetime
import logging
from typing import Any, Dict

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.loader import get_service

logger = logging.getLogger(__name__)

COLLECTOR_CONFIG_ATTRNAME = "address_configs"


@dataclass
class StormRecord:
    """Record in Storm Table"""

    messages_count: int = 0
    talkative: bool = False
    raised_alarm: bool = False
    ttl: int = 0


class StormProtection(object):
    """Message Storm Protection class

    An instance of the `Storm Protection` class is installed at the message receiving point to
    detect a situation when the number of incoming messages exceeds a certain threshold.

    The methods used are:
      `initialize' - initialize the object
      `update_messages_counter' - registration of an incoming message
      `device_is_talkative` - returns a device's "talkative" flag
      `raise_alarm' - raise an alarm

    The following settings are available:

    In the global settings:
      * storm_round_duration - duration of the verification round in seconds
      * storm_threshold_reduction - coefficient for obtaining the protection disabling threshold
      * storm_record_ttl - device's record's time to live limit

    In the settings of a specific device (SourceConfig):
      * storm_policy - storm protection policy
      * storm_threshold - threshold for the quantity of messages to enable protection


    Usage example:

    storm_protection = StormProtection(
        <round_duration>,
        <threshold_reduction>,
        <record_ttl>,
        <AlarmClass>,
    )
    storm_protection.update_messages_counter(<source>)

    For more details see docs/en/docs/dev/reference/storm_protection.md
    """

    def __init__(
        self,
        storm_round_duration: int,
        storm_threshold_reduction: float,
        storm_record_ttl: int,
        alarm_class: str,
    ):
        self.storm_round_duration = storm_round_duration
        self.storm_threshold_reduction = storm_threshold_reduction
        self.storm_record_ttl = storm_record_ttl
        self.alarm_class = alarm_class
        self.service = get_service()
        self.storm_table: Dict[str, StormRecord] = {}

    def initialize(self):
        # check for availability of address configs attribute in service
        if not hasattr(self.service, COLLECTOR_CONFIG_ATTRNAME):
            logger.error(
                "Service '%s' instance has not attribute '%s'. Storm protection will not work",
                self.service.name,
                COLLECTOR_CONFIG_ATTRNAME,
            )
            return
        pt = PeriodicCallback(self.storm_round_handler, self.storm_round_duration * 1000)
        pt.start()
        logger.info(
            "Storm protection activated and now working with round duration %s seconds",
            self.storm_round_duration,
        )

    async def storm_round_handler(self):
        to_delete = []
        talkatives_quantity = 0
        for ip in self.storm_table:
            record = self.storm_table[ip]
            cfg = getattr(self.service, COLLECTOR_CONFIG_ATTRNAME)[ip]
            # set new value to talkative flag
            if record.messages_count > cfg.storm_threshold:
                record.talkative = True
            if record.messages_count < round(cfg.storm_threshold * self.storm_threshold_reduction):
                record.talkative = False
            talkatives_quantity += int(record.talkative)
            if record.raised_alarm and not record.talkative:
                self.close_alarm(ip)
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
        logger.info(
            "End of storm protection round: found %d talkative devices", talkatives_quantity
        )

    def update_messages_counter(self, ip_address: str):
        if ip_address not in self.storm_table:
            self.storm_table[ip_address] = StormRecord()
            self.storm_table[ip_address].ttl = self.storm_record_ttl
        self.storm_table[ip_address].messages_count += 1

    def device_is_talkative(self, ip_address: str) -> bool:
        return self.storm_table[ip_address].talkative

    def raise_alarm(self, ip_address: str):
        storm_record = self.storm_table[ip_address]
        if storm_record.raised_alarm:
            return
        cfg = getattr(self.service, COLLECTOR_CONFIG_ATTRNAME)[ip_address]
        msg = {
            "$op": "raise",
            "managed_object": cfg.id,
            "alarm_class": self.alarm_class,
        }
        self.publish_message(cfg, msg)
        storm_record.raised_alarm = True

    def close_alarm(self, ip_address: str):
        cfg = getattr(self.service, COLLECTOR_CONFIG_ATTRNAME)[ip_address]
        msg = {"$op": "clear"}
        self.publish_message(cfg, msg)
        self.storm_table[ip_address].raised_alarm = False

    def publish_message(self, cfg, msg: Dict[str, Any]):
        msg["timestamp"] = datetime.datetime.now().isoformat()
        msg["reference"] = f"{self.alarm_class}{cfg.id}"
        self.service.publish(
            orjson.dumps(msg), stream=f"dispose.{config.pool}", partition=cfg.partition
        )

    def process_message(self, ip_address):
        self.update_messages_counter(ip_address)
        if self.device_is_talkative(ip_address):
            cfg = getattr(self.service, COLLECTOR_CONFIG_ATTRNAME)[ip_address]
            if cfg.storm_policy in ("R", "A"):
                # raise alarm
                self.raise_alarm(ip_address)
                logger.debug(
                    "Storm protection: SNMP-message from IP-address %s raised alarm", ip_address
                )
            if cfg.storm_policy in ("B", "A"):
                # block message
                logger.debug(
                    "Storm protection: SNMP-message from IP-address %S must be blocked", ip_address
                )
                return True
        return False
