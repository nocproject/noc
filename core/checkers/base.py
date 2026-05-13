# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import socket
import struct
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, AsyncIterable, TypeVar, Callable, ClassVar
import threading

# Third-party modules
import orjson

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.service.loader import get_service
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential
from noc.core.models.inputsources import InputSource
from noc.core.threadpool import ThreadPoolExecutor

T = TypeVar("T")

TCP_CHECK = "TCP"
FAIL_CHECK = "FAIL"
SUCCESS_CHECK = "SUCCESS"
NODATA = "NODATA"
CHECKS = []
CHECK_HISTORY_TABLE = "checkhistory"


@dataclass(frozen=True)
class MetricValue(object):
    metric_type: str
    value: float
    labels: Optional[List[str]] = None


@dataclass(frozen=True)
class DataItem(object):
    name: str
    value: Any
    scope: Optional[str] = None  # caps/attribute
    caps: Optional[str] = None  # Capability name


@dataclass(frozen=True, eq=True)
class Check(object):
    name: str  # Check name
    args: Optional[Dict[str, str]] = None
    # pool: Optional[str] = field(default=None, hash=False)  # Address Pool
    address: str = field(default=None, compare=False)  # IP Address
    port: Optional[int] = None  # TCP/UDP port
    script: Optional[str] = None
    remote_system: Optional[str] = None
    ttl: Optional[int] = None
    credential: Optional[
        Union[
            SNMPCredential,
            SNMPv3Credential,
            CLICredential,
            HTTPCredential,
        ]
    ] = field(default=None, compare=False, hash=False)

    def __str__(self):
        return f"{self.name}?{self.args}"

    def __hash__(self):
        return hash(self.key)

    @property
    def key(self) -> str:
        """Check key"""
        return f"{self.name},{self.arg}"

    @property
    def arg0(self):
        if self.args:
            return self.args.get("arg0")
        return None

    @property
    def arg(self) -> str:
        r = []
        if self.script:
            r.append(f"script={self.script}")
        if self.address:
            r.append(f"address={self.address}")
        if self.port:
            r.append(f"port={self.port}")
        if self.arg0:
            r.append(f"arg0={self.arg0}")
        if self.remote_system:
            r.append(f"remote_system={self.remote_system}")
        return "&".join(r)

    @property
    def keys(self) -> List[str]:
        """Rerurn keys fields"""
        r = []
        if self.script and self.script != "*":
            r.append("script")
        if self.address and self.address != "*":
            r.append("address")
        if self.port and self.port != "*":
            r.append("port")
        if self.arg0 and self.arg0 != "*":
            r.append("arg0")
        if self.remote_system and self.remote_system != "*":
            r.append("remote_system")
        return r

    @classmethod
    def from_string(cls, url) -> "Check":
        """
        <check>://<cred>@<address>:<port>&arg0
        :param url:
        :return:
        """

    @classmethod
    def from_dict(cls, data) -> "Check":
        credential = data.pop("credential", None)
        if credential and "snmp_ro" in credential:
            credential = SNMPCredential(**credential)
        elif credential and "context" in credential:
            credential = SNMPv3Credential(**credential)
        elif credential and "super_password" in credential:
            credential = CLICredential(**credential)
        if credential:
            data["credential"] = credential
        return Check(**data)

    @property
    def snmp_credential(self) -> Optional[SNMPCredential]:
        if isinstance(self.credential, SNMPCredential):
            return self.credential
        return None

    def set_credential(self, cred) -> "Check":
        return Check(
            name=self.name,
            args=self.args,
            address=self.address,
            port=self.port,
            script=self.script,
            credential=cred,
        )

    @property
    def has_wildcard(self) -> bool:
        """Has wilcard param"""
        return self.address == "*"

    def is_match(self, result: "CheckResult") -> bool:
        return all(getattr(result, k, None) == getattr(self, k, None) for k in self.keys)


@dataclass(frozen=True)
class CheckError(object):
    code: str  # Error code
    message: Optional[str] = None  # Description if Fail
    is_access: Optional[bool] = None  # Access to resource for credential
    is_available: Optional[bool] = None  # Port/Address is available


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool  # True - OK, False - Fail
    # For requested copied from Check
    args: Optional[Dict[str, Any]] = None  # Checked Argument
    port: Optional[int] = None
    address: Optional[str] = None
    script: Optional[str] = None
    skipped: bool = False  # Check was skipped (Example, no credential)
    error: Optional[CheckError] = None  # Set if fail
    data: Optional[List[DataItem]] = None  # Collected check data
    remote_system: Optional[str] = None  # RemoteSystem
    ttl: Optional[int] = None
    # Action: Set Profile, Credential, Send Notification (Diagnostic Header) ?
    # Metrics collected
    metrics: Optional[List[MetricValue]] = None
    # Credentials List, Return if suggests flag is set
    credential: Optional[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]] = (
        None
    )

    def __str__(self):
        return f"{self.check}?{self.args}: {self.status}"

    def __hash__(self):
        return hash(self.key)

    @property
    def key(self) -> str:
        """Check key"""
        return f"{self.check},{self.arg}"

    @property
    def arg(self) -> str:
        r = []
        if self.script:
            r.append(f"script={self.script}")
        if self.address:
            r.append(f"address={self.address}")
        if self.port:
            r.append(f"port={self.port}")
        if self.arg0:
            r.append(f"arg0={self.arg0}")
        if self.remote_system:
            r.append(f"remote_system={self.remote_system}")
        return "&".join(r)

    @property
    def arg0(self) -> str:
        if self.args:
            return self.args.get("arg0")
        return None

    @classmethod
    def from_dict(cls, v) -> "CheckResult":
        data = []
        for d in v.pop("data", None) or []:
            data.append(DataItem(**d))
        if v.get("error"):
            # if False ?
            v["error"] = CheckError(**v["error"])
        v["data"] = data
        cred = v.pop("credential", None)
        if not cred:
            return CheckResult(**v)
        if "snmp_ro" in cred:
            cred = SNMPCredential(**cred)
        elif "username" in cred and "password" not in cred:
            cred = SNMPv3Credential(**cred)
        else:
            cred = CLICredential(**cred)
        v["credential"] = cred
        return CheckResult(**v)

    @classmethod
    def from_history(
        cls,
        name,
        status,
        args,
        remote_system,
        data: Dict[str, str],
    ) -> "CheckResult":
        """Create instance from History Record"""
        r = {
            "check": name,
            "status": bool(status),
            "args": args or None,
            "port": int(data["port"]) or None,
            "address": None,
            "skipped": bool(int(data["skipped"])),
            "ttl": None,
            "remote_system": remote_system or None,
        }
        if data.get("ttl"):
            r["ttl"] = int(data["ttl"])
        if data["address"] != "0.0.0.0":
            r["address"] = data["address"]
        if data.get("error"):
            r["error"] = {
                "message": data.get("error"),
                "code": data.get("error_code"),
                "is_available": bool(int(data["is_available"])),
                "is_access": bool(int(data["is_access"])),
            }
        if data.get("data"):
            r["data"] = orjson.loads(data["data"])
        return CheckResult.from_dict(r)


class BaseChecker(object):
    """
    Base class for Checkers. Check some facts and return result
    """

    name: ClassVar[str]
    CHECKS: ClassVar[List[str]]
    USER_DISCOVERY_USE: bool = True  # Allow use in User Discovery
    _executor_lock = threading.Lock()
    _executor: Optional[ThreadPoolExecutor] = None

    def __init__(
        self,
        *,
        logger: Optional[logging.Logger] = None,
        address: Optional[str] = None,
        **kwargs,
    ):
        self.logger = PrefixLoggerAdapter(logger or logging.getLogger(self.name), self.name)
        self.address = address

    async def iter_result(self, checks: List[Check]) -> AsyncIterable[CheckResult]:
        """
        Iterate over result checks
        Args:
            checks: List checks param for run
        """
        raise NotImplementedError()

    async def run_in_executor(self, fn: Callable[[], T]) -> T:
        """Run function on executor."""
        with BaseChecker._executor_lock:
            executor = BaseChecker._executor
            if not executor:
                BaseChecker._executor = ThreadPoolExecutor(5)
                executor = BaseChecker._executor

        return await executor.submit(fn)


def register_checks(
    checks: List[CheckResult],
    source: Union[str, InputSource] = InputSource.UNKNOWN,
    managed_object: Optional[int] = None,
    service: Optional[int] = None,
):
    """Push check result to history"""
    from noc.main.models.remotesystem import RemoteSystem

    if isinstance(source, str):
        source = InputSource(source)
    source = source or InputSource.UNKNOWN
    now = datetime.datetime.now().replace(microsecond=0)
    svc = get_service()
    data = []
    for c in checks:
        r = {
            "date": now.date().isoformat(),
            "ts": now.isoformat(),
            "check_name": c.check,
            "status": c.status,
            "key": c.key,
            "ttl": c.ttl,
            "args": None,
            "port": c.port or 0,
            "address": None,
            "source": source.value,
            "script": c.script,
            "skipped": c.skipped,
            "data": "",
        }
        if c.error:
            r |= {
                "error": c.error.message,
                "error_code": c.error.code,
                "is_access": c.error.is_access,
                "is_available": c.error.is_available,
            }
        if c.address:
            r["address"] = struct.unpack("!I", socket.inet_aton(c.address))[0]
        if c.port:
            r["port"] = int(c.port)
        if c.args:
            r["args"] = {k: str(v) for k, v in c.args.items()}
        if c.data:
            r["data"] = orjson.dumps([{"name": d.name, "value": d.value} for d in c.data]).decode()
        if managed_object:
            r["managed_object"] = managed_object
        if service:
            r["service"] = service
        if c.remote_system:
            rs = RemoteSystem.get_by_name(c.remote_system)
            if rs:
                r["remote_system"] = rs.bi_id
        data += [orjson.dumps(r)]
    svc.publish(b"\n".join(data), f"ch.{CHECK_HISTORY_TABLE}")
