# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GridVCS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from collections import namedtuple
import datetime
import difflib
## Third-party modules
import pymongo
import gridfs
from mercurial.mdiff import textdiff, patch
## NOC modules
from noc.lib.nosql import get_db


Revision = namedtuple("Revision", ["id", "ts", "ft"])


class GridVCS(object):
    T_FILE = "F"
    T_BDIFF = "b"

    def __init__(self, repo):
        self.fs = gridfs.GridFS(
            get_db(), collection="noc.gridvcs.%s" % repo)
        self.files = self.fs._GridFS__files

    def get_delta(self, src, dst):
        """
        Calculate strings delta
        :param src: Source string
        :param dst: Destination string
        :return: (<type>, delta)
        """
        delta = bdiff(src, dst)
        if len(delta) >= len(dst):
            return self.T_FILE, dst
        else:
            return self.T_BDIFF, textdiff(src, dst)

    def apply_delta(self, type, src, delta):
        """
        Apply delta
        :param type: Delta type
        :param src: Source string
        :param delta: Delta
        :return: Patched string
        """
        return getattr(self, "apply_delta_%s" % type)(src, delta)

    def apply_delta_F(self, src, delta):
        """
        Raw string
        :param src:
        :param delta:
        :return:
        """
        return delta

    def apply_delta_b(self, src, delta):
        """
        Mercurial bdiff
        :param src:
        :param delta:
        :return:
        """
        return patch(src, delta)

    def put(self, object, data):
        """
        Save data
        :param object:
        :param data:
        :return:
        """
        if self.fs.exists(object=object):
            # Save delta
            # Get old version
            with self.fs.get_last_version(object=object, ft=self.T_FILE) as f:
                old_data = f.read()
            # Calculate reverse delta
            dt, delta = self.get_delta(data, old_data)
            if not delta:
                return  # Not changed
            # Save delta
            self.fs.put(delta, object=object, ts=f.upload_date, ft=dt)
            # Remove old version
            self.fs.delete(f._id)
        # Save new version
        self.fs.put(data, object=object,
            ts=datetime.datetime.now(), ft=self.T_FILE)

    def get(self, object, revision=None):
        """
        Get data
        :param object:
        :param revision:
        :return:
        """
        if not revision:
            with self.fs.get_last_version(object=object, ft=self.T_FILE) as f:
                return f.read()
        else:
            data = None
            for r in self.iter_revisions(object, reverse=True):
                with self.fs.get(r.id) as f:
                    delta = f.read()
                data = self.apply_delta(r.ft, data, delta)
                if r.id == revision.id:
                    break
            return data

    def delete(self, object):
        """
        Delete object's data and history
        :param object:
        :return:
        """
        for r in self.iter_revisions(object):
            self.fs.delete(r.id)

    def iter_revisions(self, object, reverse=False):
        """
        Get object's revision
        :param object:
        :return: List of Revisions
        """
        d = pymongo.DESCENDING if reverse else pymongo.ASCENDING
        for r in self.files.find({"object": object}).sort("ts", d):
            yield Revision(r["_id"], r["ts"], r["ft"])

    def diff(self, object, rev1, rev2):
        """
        Get unified diff between revisions
        :param object:
        :param rev1:
        :param rev2:
        :return:
        """
        src = self.get(object, rev1)
        dst = self.get(object, rev2)
        return "\n".join(
            difflib.unified_diff(src.splitlines(), dst.splitlines()))
