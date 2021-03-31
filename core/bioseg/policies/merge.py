# ----------------------------------------------------------------------
# MERGE Biosegmentation Policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Type

# NOC modules
from .base import BaseBioSegPolicy
from .eat import EatBioSegPolicy
from .feed import FeedBioSegPolicy


class MergeBioSegPolicy(BaseBioSegPolicy):
    """
    MERGE Biosegmentation. Selects proper policy according to segments' powers.

    * Eat target if attacker's power is greater
    * Feed target if attacker's power is less
    * Eat target if attacker iselder
    * Feed target otherwise
    """

    name = "merge"
    PERSISTENT_POLICY = {
        "merge": "feed",
        "keep": "keep",
        "eat": "keep",
        "feed": "feed",
        "calcify": "calcify",
    }
    FLOATING_POLICY = {
        "merge": "merge",
        "keep": "keep",
        "eat": "eat",
        "feed": "feed",
        "calcify": "calcify",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        policy_cls = self.get_effective_policy()
        self.logger.info("Effective policy is %s", policy_cls.name)
        return policy_cls(self.attacker, self.target, logger=self.logger).trial()

    def get_effective_policy(self) -> Type[BaseBioSegPolicy]:
        """
        Calculate effective policy
        :return:
        """
        attacker_power = self.get_power(self.attacker.segment)
        target_power = self.get_power(self.target.segment)
        if attacker_power > target_power:
            return EatBioSegPolicy
        if attacker_power < target_power:
            return FeedBioSegPolicy
        if self.attacker.segment.id < self.target.segment.id:
            return EatBioSegPolicy
        return FeedBioSegPolicy
