# ---------------------------------------------------------------------
# EventPlugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class EventPlugin:
    name = None

    def __init__(self, app) -> None:
        self.app = app

    def get_data(self, event, config):
        """
        Process event and return additional data
        to be added to the event data.
        Client-side configuration must be pushed as "config" key
        :param event: *Event instance
        :param config: Plugin config
        :return: dict of additional data
        """
        return {}
