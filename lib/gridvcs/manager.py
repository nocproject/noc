# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's model manager for GridVCS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from gridvcs import GridVCS
from noc.lib.fileutils import safe_rewrite


class GridVCSField(object):
    """
    Django's model manager.

    class MyModel(models.Model):
        ...
        data = GridVCSModelManager("my_repo")
        ...

    o = MyModel()
    # Place data
    o.data.write("text")
    # Get last revision
    print o.data.read()
    # Get list of revisions
    revisions = o.data.get_revisions()
    # Get revision
    print o.data.get_revision(r)
    # Get diff between revision
    print o.data.diff(rev1, rev2)
    """
    def __init__(self, repo, mirror=None):
        self.repo = repo
        self.model = None
        self.mirror = mirror

    def contribute_to_class(self, model, name):
        self.model = model
        setattr(model, name, GridVCSObjectDescriptor(self, mirror=self.mirror))


class GridVCSObjectDescriptor(object):
    def __init__(self, field, mirror=None):
        self.field = field
        self.repo = field.repo
        self.mirror = mirror
        if self.mirror:
            self.mirror = os.path.realpath(self.mirror)

    def __get__(self, instance, instance_type=None):
        mpath = None
        if self.mirror:
            mpath = os.path.join(self.mirror, unicode(instance))
            if not os.path.realpath(mpath).startswith(self.mirror):
                # Security violation
                mpath = None
        return GridVCSObjectProxy(
            self.repo, instance.id,
            mirror=mpath)


class GridVCSObjectProxy(object):
    _cache = {}

    def __init__(self, repo, id, mirror=None):
        self.repo = repo
        self.id = id
        self.mirror = mirror

    def get_gridvcs(self):
        g = self._cache.get(self.repo)
        if not g:
            g = GridVCS(self.repo)
            self._cache[self.repo] = g
        return g

    def read(self):
        return self.get_gridvcs().get(self.id)

    def write(self, data):
        r = self.get_gridvcs().put(self.id, data)
        if r and self.mirror:
            safe_rewrite(self.mirror, data)
        return r

    def get_revision(self, r):
        g = self.get_gridvcs()
        if isinstance(r, basestring):
            r = g.find_revision(self.id, r)
        return g.get(self.id, r)

    def get_revisions(self, reverse=False):
        return list(self.get_gridvcs().iter_revisions(self.id, reverse=reverse))

    def diff(self, r1, r2):
        g = self.get_gridvcs()
        if isinstance(r1, basestring):
            r1 = g.find_revision(self.id, r1)
        if isinstance(r2, basestring):
            r2 = g.find_revision(self.id, r2)
        return g.diff(self.id, r1, r2)
