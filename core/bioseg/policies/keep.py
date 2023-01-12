# ----------------------------------------------------------------------
# KEEP Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseBioSegPolicy


class KeepBioSegPolicy(BaseBioSegPolicy):
    """
    KEEP Biosegmentation policy. Do nothing, leave all as-is
    """

    name = "keep"
    PERSISTENT_POLICY = {
        "merge": "keep",
        "keep": "keep",
        "eat": "keep",
        "feed": "keep",
        "calcify": "calcify",
        "split": "split",
    }
    FLOATING_POLICY = {
        "merge": "keep",
        "keep": "keep",
        "eat": "eat",
        "feed": "feed",
        "calcify": "calcify",
        "split": "keep",
    }

    def trial(self) -> str:
        self.logger.info("Applying %s policy", self.name)
        self.logger.info("Do noting")
        return "keep"
