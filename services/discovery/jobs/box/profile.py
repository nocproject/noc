# ---------------------------------------------------------------------
# Profile check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import cachetools

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.profile.checker import ProfileChecker
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.sa.models.profile import Profile

rules_lock = threading.Lock()


class ProfileCheck(DiscoveryCheck):
    """
    Profile discovery
    """

    name = "profile"

    _rules_cache = cachetools.TTLCache(10, ttl=60)
    snmp_version_def = None

    def handler(self):
        self.logger.info("Checking profile accordance")
        profile = self.get_profile()
        if not profile:
            return  # Cannot detect
        if profile.id == self.object.profile.id:
            self.logger.info("Profile is correct: %s", profile)
        else:
            self.logger.info(
                "Profile change detected: %s -> %s. Fixing database, resetting platform info",
                self.object.profile.name,
                profile.name,
            )
            self.invalidate_neighbor_cache()
            self.object.profile = profile
            self.object.vendor = None
            self.object.plarform = None
            self.object.version = None
            self.object.save()

    def get_profile(self):
        """
        Returns profile for object, or None when not known
        """
        # Get SNMP version and community
        if hasattr(self.object, "_suggest_snmp") and self.object._suggest_snmp:
            # Use guessed community
            # as defined one may be invalid
            snmp_community = self.object._suggest_snmp[0]
            snmp_version = [
                {"snmp_v1_get": SNMP_v1, "snmp_v2c_get": SNMP_v2c}[self.object._suggest_snmp[2]]
            ]
        else:
            snmp_community = self.object.credentials.snmp_ro
            caps = self.object.get_caps()
            if caps.get("SNMP | v2c") is False or caps.get("SNMP | v2c") is None:
                snmp_version = [SNMP_v1, SNMP_v2c]
            else:
                snmp_version = [SNMP_v2c, SNMP_v1]
        checker = ProfileChecker(
            self.object.address,
            self.object.pool.name,
            logger=self.logger,
            calling_service="discovery",
            snmp_community=snmp_community,
            snmp_version=snmp_version,
        )
        profile = checker.get_profile()
        if profile:
            return profile
        # Report problem
        self.set_problem(
            alarm_class="Discovery | Guess | Profile",
            message=checker.get_error(),
            fatal=self.object.profile.id == Profile.get_generic_profile_id(),
        )
        self.logger.debug("Result %s" % self.job.problems)
        return None
