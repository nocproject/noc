# ----------------------------------------------------------------------
# Message storm protection for collectors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
import datetime

# NOC modules


STORM_CHECK_ROUND_LENGTH = 5
STORM_MESSAGES_LIMIT = 10
STORM_RESET_COUNTDOWN_VALUE = 2
STORM_DELETE_COUNTDOWN_VALUE = 20


@dataclass
class StormRecord:
    """Record it storm table"""
    messages_count: int = 0
    talkative: bool = False
    reset_countdown: int = STORM_RESET_COUNTDOWN_VALUE
    delete_countdown: int = STORM_DELETE_COUNTDOWN_VALUE


class StormProtection(object):
    """Message storm protection main functional"""
    storm_table = {}
    storm_time_start = None

    def message_should_be_blocked(self, ip_address):
        if self.storm_time_start is None:
            self.storm_time_start = datetime.datetime.now().timestamp()
        # new record
        if ip_address not in self.storm_table:
            self.storm_table[ip_address] = StormRecord()
        record: StormRecord = self.storm_table[ip_address]

        # check for new round
        time_now = datetime.datetime.now().timestamp()
        new_round = time_now - self.storm_time_start > STORM_CHECK_ROUND_LENGTH

        if new_round:
            self.storm_time_start = time_now
            # reset messages_count
            record.messages_count = 0
            # reset talkative
            if record.talkative:
                record.reset_countdown -= 1
                if record.reset_countdown <= 0:
                    record.talkative = False

        # update messages_count
        record.messages_count += 1
        # define talkative
        if record.messages_count > STORM_MESSAGES_LIMIT:
            record.talkative = True
            record.reset_countdown = STORM_RESET_COUNTDOWN_VALUE

        # cycle through all records in storm_table
        # update delete_countdown and delete record if it is old
        for ip_addr in self.storm_table:
            r: StormRecord = self.storm_table[ip_addr]
            if r.messages_count == 0:
                r.delete_countdown -= 1
                if r.delete_countdown <= 0:
                    del self.storm_table[ip_addr]

        return record.talkative


storm_protection = StormProtection()
