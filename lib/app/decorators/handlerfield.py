# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# @handler_field decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseAppDecorator
from noc.main.models.handler import Handler


class HandlerFieldDecorator(BaseAppDecorator):
    def __init__(self, cls, fields):
        self.fields = fields
        super(HandlerFieldDecorator, self).__init__(cls)

    def contribute_to_class(self):
        for f in self.fields:
            self.add_method("field_%s__label" % f, self.get_label_field(f))

    def get_label_field(self, name):
        def wrapper(app, object):
            v = getattr(object, name, None)
            if not v:
                return None  # No handler
            h = Handler.get_by_id(v)
            if h:
                return h.name
            return None

        return wrapper


def handler_field(*args):
    def wrapper(cls):
        HandlerFieldDecorator(cls, args)
        return cls

    return wrapper
