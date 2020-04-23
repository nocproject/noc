# ----------------------------------------------------------------------
# BaseApplicator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseApplicator(object):
    def __init__(self, object, confdb):
        self.object = object
        self.confdb = confdb
        self.config = {}

    def apply(self):
        pass

    def can_apply(self):
        return True
