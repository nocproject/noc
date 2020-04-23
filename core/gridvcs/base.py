# ----------------------------------------------------------------------
# GridVCS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import difflib
import zlib
import struct

# Third-party modules
import pymongo
import gridfs
import gridfs.errors
import bsdiff4
from bson import ObjectId
from typing import Tuple, Optional, Iterable

# NOC modules
from noc.core.mongo.connection import get_db
from noc.core.comp import smart_bytes, smart_text
from .revision import Revision


class GridVCS(object):
    T_FILE = "F"
    T_BDIFF = "b"
    T_BSDIFF4 = "B"
    ENCODING = "utf-8"
    DEFAULT_COMPRESS = "z"

    def __init__(self, repo):
        self.fs = gridfs.GridFS(get_db(), collection="noc.gridvcs.%s" % repo)
        self.files = self.fs._GridFS__files

    def get_delta(self, src: str, dst: str) -> Tuple[str, bytes]:
        """
        Calculate strings delta
        :param src: Source string
        :param dst: Destination string
        :return: (<type>, delta)
        """
        delta = bsdiff4.diff(src, dst)
        if len(delta) >= len(dst):
            return self.T_FILE, smart_bytes(dst)
        return self.T_BSDIFF4, delta

    @classmethod
    def apply_delta(cls, type: str, src: str, delta: bytes) -> str:
        """
        Apply delta
        :param type: Delta type
        :param src: Source string
        :param delta: Delta
        :return: Patched string
        """
        return getattr(cls, "apply_delta_%s" % type)(src, delta)

    @staticmethod
    def apply_delta_F(src: str, delta: bytes) -> str:
        """
        Raw string
        :param src:
        :param delta:
        :return:
        """
        return smart_text(delta)

    @staticmethod
    def apply_delta_b(src: str, delta: bytes) -> str:
        """
        Mercurial mdiff. Slow python implementation ported from Mercurial 0.4.
        For legacy installations support only
        :param src:
        :param delta:
        :return:
        """
        last = pos = 0
        r = []
        d_len = len(delta)

        while pos < d_len:
            p1, p2, p_len = struct.unpack(">lll", delta[pos : pos + 12])
            pos += 12
            r.append(src[last:p1])
            r.append(smart_text(delta[pos : pos + p_len]))
            pos += p_len
            last = p2
        r.append(src[last:])
        return "".join(r)

    @staticmethod
    def apply_delta_B(src: str, delta: bytes) -> str:
        """
        BSDIFF4 diff
        :param src:
        :param delta:
        :return:
        """
        return smart_text(bsdiff4.patch(src, delta))

    @classmethod
    def compress(cls, data: bytes, method: Optional[str] = None) -> bytes:
        if method:
            return getattr(cls, "compress_%s" % method)(data)
        return data

    @classmethod
    def decompress(cls, data: bytes, method: Optional[str] = None) -> bytes:
        if method:
            return getattr(cls, "decompress_%s" % method)(data)
        return data

    @staticmethod
    def compress_z(data: bytes) -> bytes:
        return zlib.compress(smart_bytes(data))

    @staticmethod
    def decompress_z(data: bytes) -> bytes:
        return zlib.decompress(smart_bytes(data))

    def put(self, object: int, data: str, ts: Optional[datetime.datetime] = None) -> bool:
        """
        Save data
        :param object: Object id
        :param data: Data to store
        :param ts: Timestamp
        :return:
        """
        if self.fs.exists(object=object):
            # Save delta
            try:
                # Get old version
                with self.fs.get_last_version(object=object, ft=self.T_FILE) as f:
                    old_data = self.decompress(f.read(), f._file.get("c"))
                # Check data has been changed
                if data == old_data:
                    return False
                # Calculate reverse delta
                dt, delta = self.get_delta(data, old_data)
                delta = self.compress(delta, self.DEFAULT_COMPRESS)
                # Save delta
                self.fs.put(
                    delta,
                    object=object,
                    ts=f.ts,
                    ft=dt,
                    encoding=self.ENCODING,
                    c=self.DEFAULT_COMPRESS,
                )
                # Remove old version
                self.fs.delete(f._id)
            except gridfs.errors.NoFile:
                pass
        # Save new version
        ts = ts or datetime.datetime.now()
        self.fs.put(
            self.compress(smart_bytes(data), self.DEFAULT_COMPRESS),
            object=object,
            ts=ts,
            ft=self.T_FILE,
            encoding=self.ENCODING,
            c=self.DEFAULT_COMPRESS,
        )
        return True

    def get(self, object: int, revision: Optional[Revision] = None) -> Optional[str]:
        """
        Get data
        :param object: Object id
        :param revision: Revision instance
        :return: Revision text
        """
        if not revision:
            try:
                with self.fs.get_last_version(object=object, ft=self.T_FILE) as f:
                    return smart_text(self.decompress(f.read(), f._file.get("c")))
            except gridfs.errors.NoFile:
                return None
        data = str()
        for r in self.iter_revisions(object, reverse=True):
            with self.fs.get(r.id) as f:
                delta = self.decompress(f.read(), f._file.get("c"))
            data = self.apply_delta(r.ft, data, delta)
            if r.id == revision.id:
                break
        return data

    def delete(self, object: int) -> None:
        """
        Delete object's data and history
        :param object:
        :return:
        """
        for r in self.iter_revisions(object):
            self.fs.delete(r.id)

    def iter_revisions(self, object: int, reverse: Optional[bool] = False) -> Iterable[Revision]:
        """
        Get object's revision
        :param object:
        :return: List of Revisions
        """
        d = pymongo.DESCENDING if reverse else pymongo.ASCENDING
        for r in self.files.find({"object": object}).sort("ts", d):
            yield Revision(r["_id"], r["ts"], r["ft"], r.get("c"), r["length"])

    def find_last_revision(self, object: int) -> Optional[Revision]:
        """
        Find last revision or return None
        :param object:
        :return:
        """
        r = self.files.find_one({"object": object}, sort=[("ts", pymongo.DESCENDING)])
        if r:
            return Revision(r["_id"], r["ts"], r["ft"], r.get("c"), r["length"])
        return None

    def find_revision(self, object: int, revision: str) -> Optional[Revision]:
        """
        :param object:
        :param revision: Revision id
        :return:
        """
        r = self.files.find_one({"object": object, "_id": ObjectId(revision)})
        if r:
            return Revision(r["_id"], r["ts"], r["ft"], r.get("c"), r["length"])
        return None

    @staticmethod
    def _unified_diff(src: str, dst: str) -> str:
        """
        Returns unified diff between src and dest

        :param src: Source text
        :param dst: Destination text
        :return: Unified diff text
        """
        return "\n".join(difflib.unified_diff(src.splitlines(), dst.splitlines(), lineterm=""))

    def diff(self, object: int, rev1: str, rev2: str) -> str:
        """
        Get unified diff between revisions
        :param object:
        :param rev1:
        :param rev2:
        :return:
        """
        src = self.get(object, rev1) or ""
        dst = self.get(object, rev2) or ""
        return self._unified_diff(src, dst)

    def mdiff(self, obj1: int, rev1: str, obj2: int, rev2: str) -> str:
        """
        Get unified diff between multiple object's revisions

        :param obj1:
        :param rev1:
        :param obj2:
        :param rev2:
        :return:
        """
        src = self.get(obj1, rev1) or ""
        dst = self.get(obj2, rev2) or ""
        return self._unified_diff(src, dst)

    def ensure_collection(self) -> None:
        self.files.create_index([("object", 1), ("ft", 1)])
