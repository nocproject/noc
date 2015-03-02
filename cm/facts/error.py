# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration Error
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Error(object):
    def __init__(self, name, obj=None):
        self.name = name
        self.obj = obj

    def __repr__(self):
        if self.obj:
            return "<Error %s: %s>" % (self.name, unicode(self.obj))
        else:
            return "<Error %s>" % self.name

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, value):
        self._obj = value
