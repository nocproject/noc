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
        self.object.validate_config(self.get_artefact("config_changed") or False)

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or "config" in checks
