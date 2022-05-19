# ---------------------------------------------------------------------
# SNMP Trap Server
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
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


class TrapServer(UDPServer):
    def __init__(self, service):
        super().__init__()
        self.service = service

    def enable_reuseport(self):
        return config.trapcollector.enable_reuseport

    def enable_freebind(self):
        return config.trapcollector.enable_freebind

    def on_read(self, data: bytes, address: Tuple[str, int]):
        metrics["trap_msg_in"] += 1
        cfg = self.service.lookup_config(address[0])
        if not cfg:
            return  # Invalid event source
        if cfg.storm_policy != "D":
            storm_protection = self.service.storm_protection
            storm_protection.update_messages_counter(address[0])
            if storm_protection.device_is_talkative(address[0]):
                if cfg.storm_policy in ("R", "A"):
                    # raise alarm
                    storm_protection.raise_alarm(address[0])
                    logger.debug(
                        f"Storm protection: SNMP-message from IP-address {address[0]} raised alarm"
                    )
                if cfg.storm_policy in ("B", "A"):
                    # block message
                    logger.debug(
                        f"Storm protection: SNMP-message from IP-address {address[0]} blocked"
                    )
                    return
            logger.debug(
                f"Storm protection: SNMP-message from IP-address {address[0]} skipped for publish"
            )
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
