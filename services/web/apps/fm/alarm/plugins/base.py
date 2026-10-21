# ---------------------------------------------------------------------
# AlarmPlugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


class AlarmPlugin:
    name = None

    def __init__(self, app) -> None:
        self.app = app

    def get_data(self, alarm, config):
        """
        Process alarm and return additional data
        to be added to the alarm data.
        Client-side configuration must be pushed as "config" key
        :param event: *Event instance
        :param config: Plugin config
        :return: dict of additional data
        """
        return {}


alarm_plugin_loader = Loader[type[AlarmPlugin]](
    bases=config.iter_customized_bases("noc.services.web.apps.fm.alarm.plugins"),
    exclude=("base",),
)
