# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseAppDecorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseAppDecorator(object):
    """
    Basic application decorator to inject new methods via .add_view
    """
    def __init__(self, cls):
        self.cls = cls
        self.contribute_to_class()

    def add_view(self, *args, **kwargs):
        self.cls.add_view(*args, **kwargs)

    def add_method(self, name, method):
        setattr(self.cls, name, method)

    def contribute_to_class(self):
        """
        Override for specific behavior
        :return:
        """
        pass

    def set_app(self, app):
        self.app = app
        self.logger = app.logger
