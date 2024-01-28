# ---------------------------------------------------------------------
# CPE Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List

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
        hints = []
        for cpe in CPE.objects.filter(
            controllers__match={"managed_object": self.object.id, "is_active": True},
            profile__in=CPEProfile.get_with_status_discovery(),
        ).read_preference(ReadPreference.SECONDARY_PREFERRED):
            if not cpe.state.is_productive:
                continue
            cpe_cache[cpe.controller.local_id] = cpe
        if not cpe_cache:
            self.logger.info("No CPE with status discovery enabled. Skipping")
            return
        bulk = []
        result: List[Dict[str, str]] = self.object.scripts.get_cpe_status(cpes=hints)
        for r in result:
            lid = r["local_id"]
            if lid not in cpe_cache:
                continue
            gid = r.get("global_id")
            cpe = cpe_cache[lid]
            if gid and cpe.global_id and gid != cpe.global_id:
                # CPE Moved
                self.logger.info("[%s] Global ID not equal. CPE moved", cpe)
            cpe.set_oper_status(r["oper_status"], bulk=bulk)
        if bulk:
            self.logger.info("%d statuses changed", len(bulk))
            CPE._get_collection().bulk_write(bulk)
