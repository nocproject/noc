# ----------------------------------------------------------------------
# Config parameters
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import logging
import pytz
from pathlib import Path
from typing import Optional, TypeVar, Generic, Any, Iterable, Dict, List, Union

# NOC modules
from noc.core.validators import is_int, is_ipv4, is_uuid
from noc.core.comp import smart_text, DEFAULT_ENCODING

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseParameter(Generic[T]):
    PARAM_NUMBER = itertools.count()

    def __init__(self, default: Optional[Union[T, str]] = None, help: Optional[str] = None):
        self.param_number = next(self.PARAM_NUMBER)
        if default is None:
            self.default = None
            self.orig_value = None
        else:
            self.orig_value = default
            self.default = self.clean(default)
        self.help = help
        self.name: Optional[str] = None  # Set by metaclass
        self.value: T = self.default  # Set by __set__ method

    def __get__(self, _instance, _owner) -> T:
        return self.value

    def __set__(self, _instance, value: Any) -> None:
        self.set_value(value)

    def set_value(self, value: Any) -> None:
        self.orig_value = value
        self.value = self.clean(value)

    def clean(self, v: Any) -> T:
        return v

    def dump_value(self) -> str:
        return str(self.value)


class StringParameter(BaseParameter[str]):
    def __init__(
        self,
        default: Optional[str] = None,
        help: Optional[str] = None,
        choices: Optional[Iterable[str]] = None,
    ):
        self.choices = set(choices) if choices else None
        super().__init__(default=default, help=help)

    def clean(self, v: Any) -> str:
        r = smart_text(v)
        if self.choices:
            if r not in self.choices:
                raise ValueError(f"Invalid value: {r}")
        return r


class SecretParameter(BaseParameter[str]):
    def __init__(
        self, default: Optional[str] = None, help: Optional[str] = None, path: Optional[Path] = None
    ):
        if path and path.exists():
            # Read defaults from file
            with open(path) as fp:
                data = fp.read().strip()
                if data:
                    default = data
        super().__init__(default=default, help=help)

    def clean(self, v: Any) -> str:
        return smart_text(v)

    def __repr__(self):
        return "****hidden****"


class UUIDParameter(BaseParameter[str]):
    def clean(self, v: Any) -> str:
        if isinstance(v, bytes):
            v = v.decode(DEFAULT_ENCODING)
        if v and not is_uuid(v):
            msg = f"Invalid UUID value: {v}"
            raise ValueError(msg)
        return v


class TimeZoneParameter(BaseParameter[pytz.BaseTzInfo]):
    def clean(self, v: Any) -> pytz.BaseTzInfo:
        try:
            return pytz.timezone(v)
        except pytz.UnknownTimeZoneError:
            msg = f"Invalid TimeZone value: {v}"
            raise ValueError(msg)


class IntParameter(BaseParameter[int]):
    def __init__(
        self,
        default: Optional[int] = None,
        help: Optional[str] = None,
        min: Optional[int] = None,
        max: Optional[int] = None,
    ):
        self.min = min
        self.max = max
        super().__init__(default=default, help=None)

    def clean(self, v: Any) -> int:
        r = int(v)
        if self.min is not None:
            if r < self.min:
                msg = f"Value is less than {self.min}"
                raise ValueError()
        if self.max is not None:
            if r > self.max:
                msg = f"Value is greater than {self.max}"
                raise ValueError(msg)
        return r


class BooleanParameter(BaseParameter[bool]):
    def clean(self, v: Any) -> bool:
        if isinstance(v, str):
            v = v.lower() in ["y", "t", "true", "yes"]
        return bool(v)


class FloatParameter(BaseParameter[float]):
    def clean(self, v: Any) -> float:
        return float(v)


class MapParameter(BaseParameter[T], Generic[T]):
    def __init__(
        self, mappings: Dict[str, T], default: Optional[str] = None, help: Optional[str] = None
    ):
        self.mappings = mappings or {}
        super().__init__(default=default, help=help)

    def clean(self, v: Any) -> T:
        try:
            return self.mappings[smart_text(v)]
        except KeyError:
            msg = f"Invalid value {v}"
            raise ValueError(msg)

    def dump_value(self) -> str:
        if not self.mappings:
            return super().dump_value()
        for mv in self.mappings:
            if self.mappings[mv] == self.value:
                return mv
        return str(self.value)


class HandlerParameter(BaseParameter[str]):
    def clean(self, v: Any) -> str:
        # h = get_handler(v)
        # if not h:
        #     raise ValueError("Invalid handler: %s" % v)
        # return h
        return str(v)


class SecondsParameter(BaseParameter[int]):
    SHORT_FORM = (
        (365 * 24 * 3600, "y"),
        (30 * 24 * 3600, "m"),
        (7 * 24 * 3600, "w"),
        (24 * 3600, "d"),
        (3600, "h"),
        (60, "M"),
    )

    SCALE = {
        "s": 1,
        "M": 60,
        "h": 3600,
        "d": 24 * 3600,
        "w": 7 * 24 * 3600,
        "m": 30 * 24 * 3600,
        "y": 365 * 24 * 3600,
    }

    def clean(self, v: Any) -> int:
        if isinstance(v, int):
            return v
        m = self.SCALE.get(v[-1], None)
        if m is None:
            m = 1
        else:
            v = v[:-1]
        try:
            return int(v) * m
        except ValueError:
            msg = "Invalid value: {v}"
            raise ValueError(msg)

    def dump_value(self) -> str:
        if self.value <= 0:
            return "0"
        for d, s in self.SHORT_FORM:
            n, r = divmod(self.value, d)
            if not r:
                return f"{n}{s}"
        return f"{self.value}s"


class BytesSizeParameter(BaseParameter[int]):
    SHORT_FORM = (
        (1099511627776, "T"),
        (1073741824, "G"),
        (1048576, "M"),
        (1024, "K"),
    )

    SCALE = {
        "B": 1,
        "K": 1024,
        "M": 1048576,
        "G": 1073741824,
        "T": 1099511627776,
    }

    def clean(self, v: Any) -> int:
        if isinstance(v, int):
            return v
        m = self.SCALE.get(v[-1], None)
        if m is None:
            m = 1
        else:
            v = v[:-1]
        try:
            return int(v) * m
        except ValueError:
            msg = f"Invalid value: {v}"
            raise ValueError(msg)

    def dump_value(self) -> str:
        if not self.value > 0:
            return "0"
        for d, s in self.SHORT_FORM:
            n, r = divmod(self.value, d)
            if not r:
                return f"{n}{s}"
        return f"{self.value}s"


class ListParameter(BaseParameter[List[T]], Generic[T]):
    def __init__(self, item: BaseParameter[T], default: Any = None, help: Optional[str] = None):
        self.item = item
        super().__init__(default=default, help=help)

    def clean(self, v: Any) -> List[T]:
        if isinstance(v, str):
            # Alter format - [value1,value2]
            if v.startswith("[") and v.endswith("]"):
                v = v[1:-1]
            v = [x.strip() for x in v.split(",")]
        return [self.item.clean(x) for x in v]


class ServiceItem(object):
    __slots__ = ["host", "port"]

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def __str__(self):
        return f"{self.host}:{self.port}"

    def __repr__(self):
        return f"<ServiceItem {self.host}:{self.port}>"

    def __contains__(self, item) -> bool:
        # @todo: Strange
        return item in f"{self.host}:{self.port}"


class ServiceParameter(BaseParameter[List[ServiceItem]]):
    """
    Resolve external service location to a list of ServiceItem.
    Service resolved at startup,
    though in future implementation it can be changed during runtime

    Resolves to empty list when service is not available.

    Arguments:
        service: Service name
        near: Resolve to nearest service
        wait: Block and wait until at least one instance of service will be available
    """

    DEFAULT_RESOLUTION_TIMEOUT = 1

    def __init__(
        self,
        service: Union[str, List[str]],
        near: bool = False,
        wait: bool = True,
        help: Optional[str] = None,
        full_result: bool = True,
        critical: bool = True,
    ):
        if isinstance(service, str):
            self.services = [service]
        else:
            self.services = service
        self.near = near
        self.wait = wait
        self.full_result = full_result
        self.critical = critical
        super().__init__(default=[], help=help)

    def __get__(self, _instance, _owner) -> List[ServiceItem]:
        if not self.value:
            from noc.core.ioloop.util import run_sync

            run_sync(self.resolve)
        return self.value

    async def async_get(self) -> List[ServiceItem]:
        if not self.value:
            await self.resolve()
        return self.value

    def set_value(self, value: Any) -> None:
        self.value = None
        self.services = [smart_text(value)]

    async def resolve(self) -> None:
        from noc.core.dcs.util import resolve_async
        from noc.core.dcs.error import ResolutionError

        if isinstance(self.services, list) and ":" in self.services[0]:
            self.value = [ServiceItem(*i.rsplit(":", 1)) for i in self.services]
            return
        if isinstance(self.services, str) and ":" in self.services:
            self.value = self.services
            return

        while True:
            for svc in self.services:
                if ServiceParameter.is_static(svc):
                    self.value = [ServiceItem(*svc.split(":"))]
                    break
                try:
                    items = await resolve_async(
                        svc,
                        wait=self.wait,
                        timeout=self.DEFAULT_RESOLUTION_TIMEOUT,
                        full_result=self.full_result,
                        near=self.near,
                        critical=self.critical,
                    )
                    if not isinstance(items, list):
                        items = [items]
                    self.value = [ServiceItem(*i.rsplit(":", 1)) for i in items]
                    break
                except ResolutionError:
                    pass
            if not self.wait or self.value:
                break

    def as_list(self) -> List[str]:
        """
        :return: List of <host>:<port>
        """
        if self.value:
            return [str(i) for i in self.value]
        return []

    def dump_value(self) -> str:
        if len(self.services) == 1:
            return self.services[0]
        return str(self.services)

    @staticmethod
    def is_static(svc):
        if ":" not in svc:
            return False
        p = svc.split(":")
        if len(p) != 2:
            return False
        return is_ipv4(p[0]) and is_int(p[1])

    def set_critical(self, critical: bool) -> None:
        """
        Change parameter's critical status

        :param critical:
        :return:
        """
        self.critical = critical
