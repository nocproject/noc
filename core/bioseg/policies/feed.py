# ----------------------------------------------------------------------
# Feed Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseBioSegPolicy


class FeedBioSegPolicy(BaseBioSegPolicy):
    """
    FEED Biosegmentation policy. Attacker looses all its objects to target.
    """

    name = "feed"
    PERSISTENT_POLICY = {
        "merge": "keep",
        "keep": "keep",
        "eat": "keep",
        "feed": "keep",
        "calcify": "calcify",
        "split": "split",
    }
    FLOATING_POLICY = {
        "merge": "eat",
        "keep": "keep",
        "eat": "eat",
        "feed": "merge",
        "calcify": "eat",
        "split": "keep",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        self.consume_objects(self.attacker, self.target)
        return "feed"
