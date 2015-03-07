# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Common system settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class BaseFact(object):
    ATTRS = []

    def __init__(self):
        self.managed_object = None

    def dump(self):
        print "- %s:" % self.__class__.__name__
        for a in self.iter_attrs():
            print "    %s: %s" % (a, getattr(self, a))

    @property
    def cls(self):
        return self.__class__.__name__.lower()

    @classmethod
    def iter_attrs(cls):
        for a in cls.ATTRS:
            if a.startswith("["):
                yield a[1:-1]
            else:
                yield a

    @classmethod
    def get_template(cls):
        r = []
        for a in cls.iter_attrs():
            if a not in cls.ATTRS:
                r += ["(multislot %s)" % a]
            else:
                r += ["(slot %s)" % a]
        return "".join(r)

    def iter_factitems(self):
        for a in self.iter_attrs():
            yield a, getattr(self, a)

    def __unicode__(self):
        return self.cls

    @property
    def managed_object(self):
        return self._managed_object

    @managed_object.setter
    def managed_object(self, value):
        self._managed_object = value

    def bind(self):
        """
        Bind to external data. Called when facts are learned by engine
        """
        pass
