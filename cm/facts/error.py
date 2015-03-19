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
    ATTRS = ["name", "obj"]
    ID = ["name", "obj"]

    def __init__(self, name, obj=None):
        super(Error, self).__init__()
        self.name = name
        self.obj = obj

    def __unicode__(self):
        if self.obj:
            return "Error %s: %s" % (self.name, unicode(self.obj))
        else:
            return "Error %s" % self.name

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, value):
        self._obj = value
