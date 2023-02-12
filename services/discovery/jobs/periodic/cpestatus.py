# ---------------------------------------------------------------------
# CPE Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.cpe import CPE
from noc.inv.models.cpeprofile import CPEProfile


class CPEStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """

    name = "cpestatus"
    required_script = "get_cpe_status"
    UNKNOWN_STATUS = "unknown"
    ACTIVE_STATUS = "active"

    def handler(self):
        has_cpe = self.has_capability("DB | CPEs")
        if not has_cpe:
            self.logger.info("No CPE discovered. Skipping cpe status check")
            return
        self.logger.info("Checking cpe statuses")
        cpe_cache = {}
        for cpe in CPE.objects.filter(
            controller=self.object.id,
            profile__in=CPEProfile.get_with_status_discovery(),
        ).read_preference(ReadPreference.SECONDARY_PREFERRED):
            cpe_cache[cpe.global_id] = cpe
        if not cpe_cache:
            self.logger.info("No CPE with status discovery enabled. Skipping")
            return
        bulk = []
        result = self.object.scripts.get_cpe_status()
        for r in result:
            if r.get("global_id") not in cpe_cache:
                continue
            cpe = cpe_cache[r["global_id"]]  # Bulk
            cpe.set_oper_status(r["status"] == "active", bulk=bulk)
        if bulk:
            CPE._get_collection().bulk_write(bulk)
