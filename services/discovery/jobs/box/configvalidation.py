# ----------------------------------------------------------------------
# ConfigValidation check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import cachetools

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.fm.models.alarmclass import AlarmClass


class ConfigValidationCheck(DiscoveryCheck):
    """
    Version discovery
    """

    name = "configvalidation"
    required_artefacts = ["config_acquired"]

    @staticmethod
    @cachetools.cached({})
    def get_ac_cm_violations():
        return AlarmClass.get_by_name("Config | Policy Violations")

    def handler(self):
        self.logger.info("Running config validation")
        is_changed = self.get_artefact("config_changed") or False
        # New ConfDB path, problems are passed via alarms
        alarms = []
        for problem in self.object.iter_validation_problems(is_changed):
            alarms += [self.get_umbrella_alarm_cfg(**problem)]
            # self.set_problem(**problem)
        if alarms:
            self.logger.info("%d problem(s) detected", len(alarms))
        else:
            self.logger.info("No problems detected")
        self.job.update_umbrella(self.get_ac_cm_violations(), alarms)

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or "config" in checks

    def get_umbrella_alarm_cfg(
        self, alarm_class=None, path=None, message=None, fatal=False, **kwargs
    ):
        """
        Getting Umbrella Alarm Cfg
        :param alarm_class: Alarm class instance or name
        :param path: Additional path
        :param message: Text message
        :param fatal: True if problem is fatal and all following checks
            must be disabled
        :param kwargs: Dict containing optional variables
        :return:
        """
        alarm_cfg = {
            "alarm_class": AlarmClass.get_by_name(alarm_class),
            "path": " | ".join(path),
            "vars": kwargs,
        }
        alarm_cfg["vars"]["message"] = message
        alarm_cfg["vars"]["path"] = path
        return alarm_cfg
