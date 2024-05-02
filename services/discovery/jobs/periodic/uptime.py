# ---------------------------------------------------------------------
# Uptime check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.fm.models.uptime import Uptime
from noc.core.mx import send_message, MessageType
from noc.config import config
from noc.core.hash import hash_int


class UptimeCheck(DiscoveryCheck):
    """
    Uptime discovery
    """

    name = "uptime"
    required_script = "get_uptime"

    def handler(self):
        mo = self.object
        if mo.object_profile.enable_periodic_discovery_snmp_check:
            self.logger.debug("Enabled 'enable_periodic_discovery_snmp_check'")
            # Check SNMP availability only on SNMP devices
            snmp_access_preference = ("S", "SC", "CS")

            if mo.access_preference in snmp_access_preference or (
                mo.access_preference == "P"
                and mo.object_profile.access_preference in snmp_access_preference
            ):
                self.logger.debug("Checking SNMP capability")
                is_snmp_available = mo.scripts.get_snmp_availability()
                self.logger.debug("Received SNMP capability %s", is_snmp_available)

                if not is_snmp_available:
                    self.logger.debug("Raise fatal error because SNMP not available")
                    self.set_problem(
                        message="SNMP access problem",
                        diagnostic="SNMP",
                        fatal=True,
                    )

        self.logger.debug("Checking uptime")
        uptime = mo.scripts.get_uptime()
        self.logger.debug("Received uptime: %s", uptime)
        if not uptime:
            return
        reboot_ts = Uptime.register(mo, uptime)
        if not reboot_ts:
            return
        self.set_artefact("reboot", True)
        if config.message.enable_reboot:
            self.logger.info("Sending reboot message to mx")
            self.send_reboot_message(reboot_ts)

    def send_reboot_message(self, ts: datetime.datetime) -> None:
        mo = self.object
        data = {
            "$version": 1,
            "ts": ts.isoformat(),
            "managed_object": {
                "id": str(mo.id),
                "name": mo.name,
                "bi_id": str(mo.bi_id),
                "address": mo.address,
                "pool": mo.pool.name,
                "profile": mo.profile.name,
                "object_profile": {
                    "id": str(mo.object_profile.id),
                    "name": mo.object_profile.name,
                },
                "administrative_domain": {
                    "id": str(mo.administrative_domain.id),
                    "name": str(mo.administrative_domain.name),
                },
                "segment": {
                    "id": str(mo.segment.id),
                    "name": str(mo.segment.name),
                },
                "x": mo.x,
                "y": mo.y,
            },
        }
        if mo.vendor:
            data["managed_object"]["vendor"] = mo.vendor.name
        if mo.platform:
            data["managed_object"]["platform"] = mo.platform.name
        if mo.version:
            data["managed_object"]["version"] = mo.version.version
        if mo.container:
            data["managed_object"]["container"] = {
                "id": str(mo.container.id),
                "name": mo.container.name,
            }
        if mo.remote_system and mo.remote_id:
            data["managed_object"]["remote_system"] = {
                "id": str(mo.remote_system.id),
                "name": mo.remote_system.name,
            }
            data["managed_object"]["remote_id"] = str(mo.remote_id)
        send_message(
            data,
            message_type=MessageType.REBOOT,
            headers=mo.get_mx_message_headers(),
            sharding_key=hash_int(mo.id) & 0xFFFFFFFF,
        )
