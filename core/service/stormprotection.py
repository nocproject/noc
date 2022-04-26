# ----------------------------------------------------------------------
# Message storm protection for collectors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
import time

# NOC modules
from noc.core.ioloop.timers import PeriodicCallback

# 60 20 0.9 10
# 5 10 0.9 5

# check round duration in seconds
STORM_CHECK_ROUND_LENGTH = 60
# limit of messages to set talkative ON
STORM_MESSAGES_LIMIT_ON = 20
# conversion rate between STORM_MESSAGES_LIMIT_ON and STORM_MESSAGES_LIMIT_OFF
STORM_MESSAGES_LIMIT_REDUCTION = 0.9
# limit of messages to set talkative OFF
STORM_MESSAGES_LIMIT_OFF = round(STORM_MESSAGES_LIMIT_ON * STORM_MESSAGES_LIMIT_REDUCTION)
# time to live of records in rounds
STORM_RECORD_TTL = 10


@dataclass
class StormRecord:
    """Record in storm table"""

    messages_count: int = 0
    talkative: bool = False
    ttl: int = STORM_RECORD_TTL


class StormProtection(object):
    """Message storm protection functionality"""

    storm_table = {}

    def initialize(self):
        pt = PeriodicCallback(self.storm_check_round, STORM_CHECK_ROUND_LENGTH * 1000)
        pt.start()

    async def storm_check_round(self):
        #print('***storm_check_round', time.time())
        to_delete = []
        for ip in self.storm_table:
            record = self.storm_table[ip]
            # set new value to talkative flag
            if record.messages_count > STORM_MESSAGES_LIMIT_ON:
                record.talkative = True
            if record.messages_count < STORM_MESSAGES_LIMIT_OFF:
                record.talkative = False
            # check time to live of record
            if record.messages_count == 0:
                record.ttl -= 1
            else:
                record.ttl = STORM_RECORD_TTL
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
        self.storm_table[ip_address].messages_count += 1

    def message_should_be_blocked(self, ip_address):
        return self.storm_table[ip_address].talkative


storm_protection = StormProtection()
