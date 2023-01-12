# ----------------------------------------------------------------------
# Eat Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseBioSegPolicy


class EatBioSegPolicy(BaseBioSegPolicy):
    """
    KEEP Biosegmentation policy. Attacker takes all objects from target.
    """

    name = "eat"
    PERSISTENT_POLICY = {
        "merge": "feed",
        "keep": "feed",
        "eat": "keep",
        "feed": "feed",
        "calcify": "calcify",
        "split": "split",
    }
    FLOATING_POLICY = {
        "merge": "feed",
        "keep": "feed",
        "eat": "merge",
        "feed": "feed",
        "calcify": "feed",
        "split": "keep",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        self.consume_objects(self.target, self.attacker)
        return "eat"
