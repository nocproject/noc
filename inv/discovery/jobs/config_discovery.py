## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.settings import config


class ConfigDiscoveryJob(MODiscoveryJob):
    name = "config_discovery"
    map_task = "get_config"

    ignored = not config.getboolean("config_discovery", "enabled")
    initial_submit_interval = config.getint("config_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("config_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("config_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        if self.to_save:
            object.save_config(result)
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {
            "object_profile__enable_config_polling": True
        }

    def can_run(self):
        return (
            super(ConfigDiscoveryJob, self).can_run()
            and self.object.object_profile.enable_config_polling
        )

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.config_polling_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.config_polling_min_interval
