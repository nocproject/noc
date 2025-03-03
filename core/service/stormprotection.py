# ----------------------------------------------------------------------
# Message Storm Protection for collector services
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from dataclasses import dataclass
import logging
from typing import Dict

# NOC modules
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.service.loader import get_service

logger = logging.getLogger(__name__)


@dataclass
class StormRecord:
    """Record in Storm Table"""

    __slots__ = ("messages_count", "verbose", "raised_alarm", "ttl", "storm_threshold")
    messages_count: int
    verbose: bool
    raised_alarm: bool
    ttl: int
    storm_threshold: int


class StormProtection(object):
    """Message Storm Protection class

    An instance of the `Storm Protection` class is installed at the message receiving point to
    detect a situation when the number of incoming messages exceeds a certain threshold.

    The methods used are:
      `initialize` - initialize the object
      `process_message` - process message according to storm policy of the device

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
    storm_protection.initialize()
    ...
    storm_protection.process_message(<source>)

    For more details see:
      docs/en/docs/dev/reference/storm_protection.md
      docs/ru/docs/dev/reference/storm_protection.md
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
        self.storm_table: Dict[str, StormRecord] = defaultdict(
            lambda: StormRecord(
                messages_count=0,
                verbose=False,
                raised_alarm=False,
                ttl=storm_record_ttl,
                storm_threshold=0,
            )
        )
        self.raise_alarm_handler = None
        self.close_alarm_handler = None

    def initialize(self):
        """
        Launches periodical callback of verification round
        """
        pt = PeriodicCallback(self.storm_round_handler, self.storm_round_duration * 1000)
        pt.start()
        logger.info(
            "Storm protection activated and now working with round duration %s seconds",
            self.storm_round_duration,
        )

    async def storm_round_handler(self):
        to_delete = []
        verbose_devices_quantity = 0
        for ip, record in self.storm_table.items():
            # set new value to verbose flag
            if record.verbose:
                record.verbose = record.messages_count >= round(
                    record.storm_threshold * self.storm_threshold_reduction
                )
            else:
                record.verbose = record.messages_count > record.storm_threshold
            verbose_devices_quantity += int(record.verbose)
            if record.raised_alarm and not record.verbose:
                self.close_alarm(ip)
            # check time to live of record
            if record.messages_count:
                record.ttl = self.storm_record_ttl
            else:
                record.ttl -= 1
            if record.ttl <= 0:
                to_delete.append(ip)
            else:
                # reset messages count
                record.messages_count = 0
        # delete old records
        for ip in to_delete:
            del self.storm_table[ip]
        logger.debug(
            "End of storm protection round: found %d verbose devices", verbose_devices_quantity
        )

    def register_message(self, ip_address: str, storm_threshold: int):
        self.storm_table[ip_address].storm_threshold = storm_threshold
        self.storm_table[ip_address].messages_count += 1

    def device_is_verbose(self, ip_address: str) -> bool:
        return self.storm_table[ip_address].verbose

    def raise_alarm(self, ip_address: str):
        storm_record = self.storm_table[ip_address]
        if storm_record.raised_alarm:
            return
        self.raise_alarm_handler(ip_address)
        storm_record.raised_alarm = True

    def close_alarm(self, ip_address: str):
        self.close_alarm_handler(ip_address)
        self.storm_table[ip_address].raised_alarm = False

    def process_message(self, ip_address: str, address_config) -> bool:
        """
        Performs necessary actions with message according to storm policy of the device,
        i.e. raise alarm.
        Return True if message must be blocked in service and False otherwise.
        :param ip_address:
        :param address_config:
        :return:
        """
        self.register_message(ip_address, address_config.storm_threshold)
        if self.device_is_verbose(ip_address):
            if address_config.storm_policy in ("R", "A"):
                # raise alarm
                self.raise_alarm(ip_address)
                logger.debug(
                    "Storm protection: SNMP-message from IP-address %s raised alarm", ip_address
                )
            if address_config.storm_policy in ("B", "A"):
                # block message
                logger.debug(
                    "Storm protection: SNMP-message from IP-address %S must be blocked", ip_address
                )
                return True
        return False
