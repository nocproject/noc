# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Configuration Error
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Configuration Error
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseFact


class Error(BaseFact):
<<<<<<< HEAD
    ATTRS = ["type", "obj", "msg", "rule"]
    ID = ["type", "obj", "msg"]

    def __init__(self, type, obj=None, msg=None, rule=None):
=======
    ATTRS = ["type", "obj", "msg"]
    ID = ["type", "obj", "msg"]

    def __init__(self, type, obj=None, msg=None):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        super(Error, self).__init__()
        self.type = type
        self.obj = obj
        self.msg = msg
<<<<<<< HEAD
        self.rule = rule
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def __unicode__(self):
        if self.obj:
            return "Error %s: %s" % (self.type, unicode(self.obj))
        else:
            return "Error %s" % self.type

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, value):
        self._obj = value

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value or None
<<<<<<< HEAD

    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, value):
        self._rule = value or None
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
