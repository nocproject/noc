# ----------------------------------------------------------------------
# ConfigValidation check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
    umbrella_cls = "Config | Policy Violations"

    def handler(self):
        self.logger.info("Running config validation")
        is_changed = self.get_artefact("config_changed") or False
        # New ConfDB path, problems are passed via alarms
        problems = []
        for problem in self.object.iter_validation_problems(is_changed):
            problems += [problem]
            # self.set_problem(**problem)
        if problems:
            self.logger.info("%d problem(s) detected", len(problems))
        else:
            self.logger.info("No problems detected")
        self.job.update_alarms(
            self.umbrella_cls, problems, group_reference=f"g:c:{self.object.id}:{self.umbrella_cls}"
        )

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or "config" in checks
