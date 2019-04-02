# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseApplicator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseApplicator(object):
    def __init__(self, confdb):
        self.confdb = confdb
        self.config = {}

    def apply(self, object):
        pass
