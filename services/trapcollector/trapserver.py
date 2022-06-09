# ---------------------------------------------------------------------
# SNMP Trap Server
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import time
from typing import Tuple
import codecs

# NOC modules
from noc.core.ioloop.udpserver import UDPServer
from noc.core.escape import fm_escape
from noc.core.snmp.trap import decode_trap
from noc.config import config
from noc.core.perf import metrics


logger = logging.getLogger(__name__)

STORM_CHECK_ROUND_LENGTH = 5
STORM_MESSAGES_LIMIT = 10
STORM_RESET_COUNTDOWN_VALUE = 2
STORM_DELETE_COUNTDOWN_VALUE = 20

storm_table = {}
storm_time_start = None


class StormRecord(object):
    def __init__(self):
        self.messages_count: int = 0
        self.talkative: bool = False
        self.reset_countdown: int = STORM_RESET_COUNTDOWN_VALUE
        self.delete_countdown: int = STORM_DELETE_COUNTDOWN_VALUE


# Message storm protection
def message_should_be_blocked(ip_address):
    global storm_table
    global storm_time_start

    if storm_time_start is None:
        storm_time_start = datetime.datetime.now().timestamp()
    # new record
    if ip_address not in storm_table:
        storm_table[ip_address] = StormRecord()
    record: StormRecord = storm_table[ip_address]

    # check for new round
    time_now = datetime.datetime.now().timestamp()
    new_round = time_now - storm_time_start > STORM_CHECK_ROUND_LENGTH

    if new_round:
        storm_time_start = time_now
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
    for ip_addr in storm_table:
        r: StormRecord = storm_table[ip_addr]
        if r.messages_count == 0:
            r.delete_countdown -= 1
            if r.delete_countdown <= 0:
                del storm_table[ip_addr]

    return record.talkative


class TrapServer(UDPServer):
    def __init__(self, service):
        super().__init__()
        self.service = service

    def enable_reuseport(self):
        return config.trapcollector.enable_reuseport

    def enable_freebind(self):
        return config.trapcollector.enable_freebind

    def on_read(self, data: bytes, address: Tuple[str, int]):
        if message_should_be_blocked(address[0]):
            print('Сообщение блокировано ---')
            return

        metrics["trap_msg_in"] += 1
        cfg = self.service.lookup_config(address[0])
        if not cfg:
            return  # Invalid event source
        if cfg.storm_policy != "D":
            need_block = self.service.storm_protection.process_message(address[0])
            if need_block:
                return
        try:
            community, varbinds, raw_data = decode_trap(data, raw=self.service.mx_message)
        except Exception as e:
            metrics["error", ("type", "decode_failed")] += 1
            logger.error("Failed to decode trap: %s", codecs.encode(data, "hex"))
            logger.error("Decoder error: %s", e)
            return
        # @todo: Check trap community
        # Get timestamp
        ts = int(time.time())
        # Build body
        body = {"source": "SNMP Trap", "collector": config.pool}
        body.update(varbinds)
        body = {k: fm_escape(body[k]) for k in body}
        self.service.register_message(cfg, ts, body, raw_data, address[0])
