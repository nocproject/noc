# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Common system settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class BaseFact(object):
    ATTRS = []

    def dump(self):
        print "- %s:" % self.__class__.__name__
        for a in self.ATTRS:
            print "    %s: %s" % (a, getattr(self, a))

    @property
    def cls(self):
        return self.__class__.__name__

    def __unicode__(self):
        return self.cls
