# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmPlugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class AlarmPlugin(object):
    name = None

    def __init__(self, app):
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
