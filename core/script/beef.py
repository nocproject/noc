# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Beef API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import namedtuple
# Third-party modules
import ujson
import six

Box = namedtuple("Box", ["vendor", "platform", "version"])
CLIFSM = namedtuple("CLIFSM", ["state", "reply"])
CLI = namedtuple("CLI", ["names", "request", "reply"])
MIB = namedtuple("MIB", ["oid", "value"])


class Beef(object):
    def __init__(self):
        self.version = None
        self.uuid = None
        self.spec = None
        self.box = None
        self.changed = None
        self.description = None
        self.cli_fsm = None
        self.cli = None
        self.mib = None
        self.mib_encoding = None

    @classmethod
    def from_json(cls, data):
        if isinstance(data, six.string_types):
            data = ujson.loads(data)
        version = data.get("version", "1")
        decoder = "decode_v%s" % version
        beef = Beef()
        if not hasattr(cls, decoder):
            raise ValueError("Unknown beef version '%s'" % version)
        getattr(beef, decoder)(data)
        return beef

    @staticmethod
    def get_or_die(d, k):
        if k not in d:
            raise ValueError("Missed '%s' key" % k)
        return d[k]

    def decode_v1(self, data):
        self.version = self.get_or_die(data, "version")
        self.uuid = self.get_or_die(data, "uuid")
        self.spec = self.get_or_die(data, "spec")
        box = self.get_or_die(data, "box")
        self.box = Box(
            vendor=self.get_or_die(box, "vendor"),
            platform=self.get_or_die(box, "platform"),
            version=self.get_or_die(box, "version")
        )
        self.changed = self.get_or_die(data, "changed")
        self.description = data.get("description") or ""
        self.cli_fsm = [
            CLIFSM(
                state=self.get_or_die(d, "state"),
                reply=[str(n) for n in self.get_or_die(d, "reply")]
            ) for d in self.get_or_die(data, "cli_fsm")
        ]
        self.cli = [
            CLI(
                names=[n for n in self.get_or_die(d, "names")],
                request=self.get_or_die(d, "request"),
                reply=[str(n) for n in self.get_or_die(d, "reply")]
            ) for d in self.get_or_die(data, "cli")
        ]
        self.mib_encoding = self.get_or_die(data, "mib_encoding")
        self.mib = [
            MIB(
                oid=self.get_or_die(d, "oid"),
                value=self.get_or_die(d, "value")
            ) for d in self.get_or_die(data, "mib")
        ]

    def get_data(self):
        return {
            "version": "1",
            "uuid": self.uuid,
            "spec": self.spec,
            "box": {
                "vendor": self.box.vendor,
                "platform": self.box.platform,
                "version": self.box.version
            },
            "changed": self.changed,
            "description": self.description,
            "cli_fsm": [{
                "state": d.state,
                "reply": d.reply
            } for d in self.cli_fsm],
            "cli": [{
                "names": d.names,
                "request": d.request,
                "reply": d.reply
            } for d in self.cli],
            "mib_encoding": "base64",
            "mib": [{
                "oid": d.oid,
                "value": d.value.encode("base64").strip()
            } for d in self.mib]
        }

    @staticmethod
    def compress_gzip(data):
        import gzip
        f = six.StringIO()
        with gzip.GzipFile(mode="wb", compresslevel=9, fileobj=f) as z:
            z.write(data)
        return f.getvalue()

    @staticmethod
    def compress_bz2(data):
        import bz2
        return bz2.compress(data)

    @staticmethod
    def decompress_gzip(data):
        import gzip
        f = six.StringIO(data)
        with gzip.GzipFile(mode="rb", compresslevel=9, fileobj=f) as z:
            return z.read()

    @staticmethod
    def decompress_bz2(data):
        import bz2
        return bz2.decompress(data)

    def save(self, storage, path):
        """
        Write beef to external storage. Compression depends on extension.
        Following extensions are supported:
        * .json - JSON without compression
        * .json.gz - JSON with gzip compression
        * .json.bz2 - JSON with bzip2 compression

        :param storage: ExtStorage instance
        :param path: Beef path
        :return: Compressed, Uncompressed sizes
        """
        data = ujson.dumps(self.get_data())
        usize = len(data)
        dir_path = os.path.dirname(path)
        if path.endswith(".gz"):
            data = self.compress_gzip(data)
        elif path.endswith(".bz2"):
            data = self.compress_bz2(data)
        csize = len(data)
        try:
            with storage.open_fs() as fs:
                if dir_path and dir_path != "/":
                    fs.makedirs(dir_path, recreate=True)
                fs.setbytes(path, bytes(data))
        except storage.Error as e:
            raise IOError(str(e))
        return csize, usize

    @classmethod
    def load(cls, storage, path):
        """
        Load beef from storage
        :param storage:
        :param path:
        :return:
        """
        try:
            with storage.open_fs() as fs:
                data = fs.getbytes(unicode(path))
        except storage.Error as e:
            raise IOError(str(e))
        if path.endswith(".gz"):
            data = cls.decompress_gzip(data)
        elif path.endswith(".json.bz2"):
            data = cls.decompress_bz2(data)
        return Beef.from_json(data)
