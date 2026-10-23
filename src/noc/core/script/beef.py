# ----------------------------------------------------------------------
# Beef API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple
import bisect
import itertools
import codecs
from io import StringIO

# Third-party modules
import orjson
from typing import NamedTuple

# NOC modules
from noc.core.comp import smart_text, smart_bytes
from noc.main.models.extstorage import ExtStorage

Box = namedtuple("Box", ["profile", "vendor", "platform", "version"])
CLIFSM = namedtuple("CLIFSM", ["state", "reply"])
CLI = namedtuple("CLI", ["names", "request", "reply"])
MIB = namedtuple("MIB", ["oid", "value"])


class BoxData(NamedTuple):
    profile: str
    vendor: str
    platform: str
    version: str


class CLIFSMData(NamedTuple):
    state: str
    reply: list[bytes]


class CLIData(NamedTuple):
    names: list[str]
    request: bytes
    reply: list[bytes]


class MIBData(NamedTuple):
    oid: str
    value: bytes


class Beef:
    def __init__(self) -> None:
        self.version: str | None = None
        self.uuid = None
        self.spec = None
        self.box: BoxData | None = None
        self.changed = None
        self.description: str | None = None
        self.cli_fsm: list[CLIFSMData] | None = None
        self.cli: list[CLIData] | None = None
        self.mib: list[MIBData] | None = None
        self.mib_encoding: str | None = None
        self.mib_oid_values: dict[str, bytes] | None = None
        self.mib_oids: list[tuple[int]] | None = None

    @classmethod
    def from_json(cls, data):
        if isinstance(data, str):
            data = orjson.loads(data)
        version = data.get("version", "1")
        decoder = f"decode_v{version}"
        beef = Beef()
        if not hasattr(cls, decoder):
            raise ValueError(f"Unknown beef version '{version}'")
        getattr(beef, decoder)(data)
        return beef

    @staticmethod
    def get_or_die(d, k):
        if k not in d:
            raise ValueError(f"Missed '{k}' key")
        return d[k]

    def decode_v1(self, data):
        self.version = self.get_or_die(data, "version")
        self.uuid = self.get_or_die(data, "uuid")
        self.spec = self.get_or_die(data, "spec")
        box = self.get_or_die(data, "box")
        self.box = Box(
            profile=self.get_or_die(box, "profile"),
            vendor=self.get_or_die(box, "vendor"),
            platform=self.get_or_die(box, "platform"),
            version=self.get_or_die(box, "version"),
        )
        self.changed = self.get_or_die(data, "changed")
        self.description = data.get("description") or ""
        self.cli_fsm = [
            CLIFSM(
                state=self.get_or_die(d, "state"),
                reply=[smart_bytes(n) for n in self.get_or_die(d, "reply")],
            )
            for d in self.get_or_die(data, "cli_fsm")
        ]
        self.cli = [
            CLI(
                names=list(self.get_or_die(d, "names")),
                request=smart_bytes(self.get_or_die(d, "request")),
                reply=[smart_bytes(n) for n in self.get_or_die(d, "reply")],
            )
            for d in self.get_or_die(data, "cli")
        ]
        self.mib_encoding = self.get_or_die(data, "mib_encoding")
        self.mib = [
            MIB(oid=self.get_or_die(d, "oid"), value=smart_bytes(self.get_or_die(d, "value")))
            for d in self.get_or_die(data, "mib")
        ]
        self._mib_decoder = getattr(self, f"mib_decode_{self.mib_encoding}")
        self.cli_encoding = self.get_or_die(data, "cli_encoding")
        self._cli_decoder = getattr(self, f"cli_decode_{self.cli_encoding}")

    def get_data(self, decode=False):
        return {
            "version": "1",
            "uuid": self.uuid,
            "spec": self.spec,
            "box": {
                "profile": self.box.profile,
                "vendor": self.box.vendor,
                "platform": self.box.platform,
                "version": self.box.version,
            },
            "changed": self.changed,
            "description": self.description,
            "cli_encoding": self.cli_encoding,
            "cli_fsm": [
                {
                    "state": d.state,
                    "reply": [
                        smart_text(reply if not decode else self._cli_decoder(reply))
                        for reply in d.reply
                    ],
                }
                for d in self.cli_fsm
            ],
            "cli": [
                {
                    "names": d.names,
                    "request": smart_text(
                        d.request
                    ),  # In self.cli is bytes. That need for iter_cli
                    "reply": [
                        smart_text(reply if not decode else self._cli_decoder(reply))
                        for reply in d.reply
                    ],
                }
                for d in self.cli
            ],
            "mib_encoding": self.mib_encoding,
            "mib": [
                {
                    "oid": d.oid,
                    "value": smart_text(d.value if not decode else self._mib_decoder(d.value)),
                }
                for d in self.mib
            ],
        }

    @staticmethod
    def compress_gzip(data: bytes) -> bytes:
        import gzip

        f = StringIO()
        with gzip.GzipFile(mode="wb", compresslevel=9, fileobj=f) as z:
            z.write(data)
        return f.getvalue()

    @staticmethod
    def compress_bz2(data: bytes) -> bytes:
        import bz2

        return bz2.compress(data)

    @staticmethod
    def decompress_gzip(data: bytes) -> bytes:
        import gzip

        f = StringIO(data)
        with gzip.GzipFile(mode="rb", compresslevel=9, fileobj=f) as z:
            return z.read()

    @staticmethod
    def decompress_bz2(data: bytes) -> bytes:
        import bz2

        return bz2.decompress(data)

    def save(self, storage: ExtStorage, path: str) -> tuple[int, int]:
        """Write beef to external storage. Compression depends on extension.
        Following extensions are supported:
        * .json - JSON without compression
        * .json.gz - JSON with gzip compression
        * .json.bz2 - JSON with bzip2 compression

        Args:
            storage: ExtStorage instance
            path: Beef path

        Returns:
            Compressed, Uncompressed sizes
        """
        data = orjson.dumps(self.get_data())
        usize = len(data)
        if path.endswith(".gz"):
            data = self.compress_gzip(data)
        elif path.endswith(".bz2"):
            data = self.compress_bz2(data)
        csize = len(data)
        try:
            storage.write_bytes(path, data)
        except storage.StorageErrors as e:
            raise OSError(str(e)) from e
        return csize, usize

    @classmethod
    def load(cls, storage, path):
        """Load beef from storage

        Args:
            storage
            path
        """
        if isinstance(storage, str):
            # Load from URL
            try:
                with ExtStorage.from_url(storage) as blob:
                    data = blob[smart_text(path)]
            except ExtStorage.StorageErrors as e:
                raise OSError(str(e)) from e
        else:
            # Load from external storage
            try:
                data = storage.read_bytes(path)
            except ExtStorage.StorageErrors as e:
                raise OSError(str(e)) from e
        if path.endswith(".gz"):
            data = cls.decompress_gzip(data)
        elif path.endswith(".json.bz2"):
            data = cls.decompress_bz2(data)
        return Beef.from_json(smart_text(data))

    def iter_fsm_state_reply(self, state: str) -> bytes:
        """Iterate fsm states

        Args:
            state
        """
        for fsm in self.cli_fsm:
            if fsm.state == state:
                for reply in fsm.reply:
                    yield self._cli_decoder(reply)
                break

    def iter_cli_reply(self, command: bytes) -> bytes:
        """Iterate fsm states

        Args:
            command
        """
        # typo
        # cmd = smart_bytes(command)
        cmd = command
        found = False
        for c in self.cli:
            if c.request == cmd:
                for reply in c.reply:
                    yield self._cli_decoder(reply)
                found = True
                break
        if not found:
            raise KeyError(b"Command not found")

    @staticmethod
    def mib_decode_base64(value: bytes) -> bytes:
        """Decode base64

        Args:
            value
        """
        return codecs.decode(value, "base64")

    @staticmethod
    def mib_decode_hex(value):
        """Decode base64

        Args:
            value
        """
        return value.decode("hex")

    @staticmethod
    def cli_decode_quopri(value: bytes) -> bytes:
        """Decode quoted-printable

        Args:
            value
        """
        return codecs.decode(value, "quopri")

    def get_mib_oid_values(self):
        if self.mib_oid_values is None:
            self.mib_oid_values = {m.oid: m.value for m in self.mib}
        return self.mib_oid_values

    def get_mib_value(self, oid: str) -> bytes | None:
        """Lookup mib and return oid value

        Args:
            oid

        Returns:
            Binary OID data or None
        """
        v = self.get_mib_oid_values().get(oid)
        if v is None:
            return None
        return self._mib_decoder(v)

    def get_mib_oids(self):
        """Return sorted list of MIB oids"""
        if self.mib_oids is None:
            self.mib_oids = sorted(tuple(int(c) for c in m.oid.split(".")) for m in self.mib)
        return self.mib_oids

    def iter_mib_oids(self, oid):
        """Generator yielding all consequentive oids

        Args:
            oid
        """
        start = tuple(int(c) for c in oid.split("."))
        oids = self.get_mib_oids()
        i = bisect.bisect_left(oids, start)
        for o in itertools.islice(oids, i, len(oids)):
            yield ".".join(str(c) for c in o)
