# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CPE check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class CPECheck(DiscoveryCheck):
    """
    CPE check
    @todo: Remove stale CPE
    """
    name = "cpe"
    required_script = "get_cpe"
    required_capabilities = ["CPE | Controller"]

    def handler(self):
        self.logger.info("Checking CPEs")
        now = datetime.datetime.now()
        result = self.object.scripts.get_cpe()
        for cpe in result:
            if cpe["status"] != "active":
                self.logger.debug(
                    "[%s|%s] CPE status is '%s'. Skipping",
                    cpe["id"], cpe["global_id"], cpe["status"]
                )
                continue
            mo = self.find_cpe(cpe["global_id"])
            if mo:
                changes = self.update_if_changed(mo, {
                    "controller": self.object,
                    "local_cpe_id": cpe["id"],
                    "global_cpe_id": cpe["global_id"],
                    "address": cpe["ip"],
                    "last_seen": now
                })
                if changes:
                    self.logger.info(
                        "[%s|%s] Changed: %s",
                        cpe["id"], cpe["global_id"],
                        ", ".join("%s='%s'" % c for c in changes)
                    )
            else:
                name = cpe.get("name") or "cpe-%s" % cpe["global_id"]
                if ManagedObject.objects.filter(name=name).exists():
                    name = "cpe-%s" % cpe["global_id"]
                self.logger.info(
                    "[%s|%s] Created CPE %s",
                    cpe["id"], cpe["global_id"], name
                )
                mo = ManagedObject(
                    name=name,
                    pool=self.object.pool,
                    profile=Profile.get_generic_profile_id(),
                    object_profile=self.object.object_profile.cpe_profile or self.object.object_profile,
                    administrative_domain=self.object.administrative_domain,
                    scheme=self.object.scheme,
                    segment=self.object.segment,
                    auth_profile=self.object.object_profile.cpe_auth_profile or self.object.auth_profile,
                    address=cpe.get("ip") or "0.0.0.0",
                    controller=self.object,
                    last_seen=now,
                    local_cpe_id=cpe["id"],
                    global_cpe_id=cpe["global_id"]
                )
                mo.save()

    @classmethod
    def find_cpe(cls, global_id):
        try:
            return ManagedObject.objects.get(global_cpe_id=global_id)
        except ManagedObject.DoesNotExist:
            return None
