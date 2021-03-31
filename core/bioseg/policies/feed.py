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
    }
    FLOATING_POLICY = {
        "merge": "eat",
        "keep": "keep",
        "eat": "eat",
        "feed": "merge",
        "calcify": "eat",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        if self.attacker.segment.profile.is_persistent and self.attacker.object:
            self.consume_object(self.attacker.object, self.target.segment)
        else:
            self.consume_objects(self.attacker.segment, self.target.segment)
        return "feed"
