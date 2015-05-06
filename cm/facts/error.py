# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration Error
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class Error(BaseFact):
    ATTRS = ["type", "obj", "msg"]
    ID = ["type", "obj", "msg"]

    def __init__(self, type, obj=None, msg=None):
        super(Error, self).__init__()
        self.type = type
        self.obj = obj
        self.msg = msg

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
