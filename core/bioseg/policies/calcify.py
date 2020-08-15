# ----------------------------------------------------------------------
# CALCIFY Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseBioSegPolicy


class CalcifyBioSegPolicy(BaseBioSegPolicy):
    """
    Calcify Biosegmentation policy.
    """

    name = "calcify"
    PERSISTENT_POLICY = {
        "merge": "keep",
        "keep": "keep",
        "eat": "keep",
        "feed": "keep",
        "calcify": "calcify",
    }
    FLOATING_POLICY = {
        "merge": "keep",
        "keep": "keep",
        "eat": "keep",
        "feed": "feed",
        "calcify": "calcify",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        if not self.attacker.profile.calcified_profile:
            self.logger.info("Cannot calcify without calcified profile")
            raise ValueError("Cannot calcify without calcified profile")
        if not self.attacker.profile.calcified_profile.is_persistent:
            self.logger.info("Calcified profile must be persistent")
            raise ValueError("Calcified profile must be persistent")
        self.logger.info("Calcified with profile '%s'" % self.attacker.profile.calcified_profile)
        # Change segment profile to calcified one
        self.attacker.profile = self.attacker.profile.calcified_profile
        # Attach to target as child
        self.attacker.parent = self.target
        self.attacker.save()
        # Schedule uplink rebuilding
        self.refresh_topology(self.attacker)
        return "calcify"
