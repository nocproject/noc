# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfigValidation check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class ConfigValidationCheck(DiscoveryCheck):
    """
    Version discovery
    """

    name = "configvalidation"
    required_artefacts = ["config_acquired"]

    def handler(self):
        self.logger.info("Running config validation")
        is_changed = self.get_artefact("config_changed") or False
        # Legacy CLIPS path, problems are passed via Facts
        self.object.validate_config(is_changed)
        # New ConfDB path, problems are passed via alarms
        n = 0
        for problem in self.object.iter_validation_problems(is_changed):
            self.set_problem(**problem)
            n += 1
        if n:
            self.logger.info("%d problem(s) detected", n)
        else:
            self.logger.info("No problems detected")

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or "config" in checks
