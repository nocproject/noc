# ----------------------------------------------------------------------
# Django's model manager for GridVCS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from .base import GridVCS

logger = logging.getLogger(__name__)


class GridVCSField(object):
    """
    Django's model manager.

    class MyModel(NOCModel):
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

    def __init__(self, repo):
        self.repo = repo
        self.model = None

    def contribute_to_class(self, model, name):
        """
        Initialize Django's model
        """
        self.model = model
        setattr(model, name, GridVCSObjectDescriptor(self))

    def __get__(self, instance, owner):
        """
        Mongoengine shortcut
        """
        return GridVCSObjectProxy(self.repo, instance.id)


class GridVCSObjectDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.repo = field.repo

    def __get__(self, instance, instance_type=None):
        return GridVCSObjectProxy(self.repo, instance.id)


class GridVCSObjectProxy(object):
    _cache = {}

    def __init__(self, repo, id):
        self.repo = repo
        self.id = id

    def get_gridvcs(self):
        g = self._cache.get(self.repo)
        if not g:
            g = GridVCS(self.repo)
            self._cache[self.repo] = g
        return g

    def read(self):
        return self.get_gridvcs().get(self.id)

    def write(self, data):
        return self.get_gridvcs().put(self.id, data)

    def delete(self):
        return self.get_gridvcs().delete(self.id)

    def get_revision(self, r):
        g = self.get_gridvcs()
        if isinstance(r, str):
            r = g.find_revision(self.id, r)
        return g.get(self.id, r)

    def get_last_revision(self):
        g = self.get_gridvcs()
        return g.find_last_revision(self.id)

    def has_revision(self, r):
        """
        Check config has revision

        :param r: String containing revision id
        :return: True if object has revision
        """
        g = self.get_gridvcs()
        return bool(g.find_revision(self.id, r))

    def get_revisions(self, reverse=False):
        return list(self.get_gridvcs().iter_revisions(self.id, reverse=reverse))

    def diff(self, r1, r2):
        g = self.get_gridvcs()
        if isinstance(r1, str):
            r1 = g.find_revision(self.id, r1)
        if isinstance(r2, str):
            r2 = g.find_revision(self.id, r2)
        return g.diff(self.id, r1, r2)

    def mdiff(self, r1, obj2, r2):
        g = self.get_gridvcs()
        if isinstance(r1, str):
            r1 = g.find_revision(self.id, r1)
        if isinstance(r2, str):
            r2 = g.find_revision(obj2, r2)
        return g.mdiff(self.id, r1, obj2, r2)
