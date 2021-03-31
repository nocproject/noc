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
    }
    FLOATING_POLICY = {
        "merge": "feed",
        "keep": "feed",
        "eat": "merge",
        "feed": "feed",
        "calcify": "feed",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        if self.target.segment.profile.is_persistent and self.target.object:
            self.consume_object(self.target.object, self.attacker.segment)
        else:
            self.consume_objects(self.target.segment, self.attacker.segment)
        return "eat"
