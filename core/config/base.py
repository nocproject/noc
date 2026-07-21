# ----------------------------------------------------------------------
# Configuration class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import importlib
import inspect
import re
import os
from typing import Iterable, Any
import warnings

# NOC modules
from .params import BaseParameter

DEFAULT_CONFIG = "yaml:///opt/noc/etc/tower.yml,yaml:///opt/noc/etc/settings.yml,env:///NOC"
DEFAULT_DUMP_URL = "yaml://"


class ConfigurationError(Exception):
    """Configuration error."""


class ConfigSectionBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._params = {}
        for k in attrs:
            if isinstance(attrs[k], BaseParameter):
                cls._params[k] = attrs[k]
                cls._params[k].name = k
            if isinstance(attrs[k], ConfigSectionBase):
                for pname, attr in attrs[k]._params.items():
                    cls._params[f"{k}.{pname}"] = attr
                    cls._params[f"{k}.{pname}"].name = f"{k}.{pname}"
        return cls


class ConfigSection(metaclass=ConfigSectionBase):
    pass


class BaseRewrite:
    """Rewrite configuration parameter."""

    def __init__(self, /, deprecation: type[Warning] | None = None) -> None:
        self.deprecation = deprecation

    def rewrite(self, key: str, value: Any) -> tuple[str, Any] | None:
        """
        Rewrite configuration parameter.

        Args:
            key: dot-separated parameter name.
            value: parameter value.

        Returns:
            (key, value): Rewritten key-value pair.
            None: Value must be dropped.
        """
        raise NotImplementedError

    def reverse_rewrite(self, key: str) -> str | None:
        """
        Rewrite name back.

        If rule rewrites parameter name, find the name
        which will be rewriten to given.

        Args:
            key: Target name.

        Returns:
            None: if name is not a result of rewriting.
            old value: which can be rewriten to given one.
        """
        return None


class PrefixRewrite(BaseRewrite):
    """Rewrite parameter's prefix."""

    def __init__(
        self, prefix: str, rewrite_to: str, /, deprecation: type[Warning] | None = None
    ) -> None:
        super().__init__(deprecation=deprecation)
        self.prefix = f"{prefix}."
        self.rewrite_to = f"{rewrite_to}."

    def rewrite(self, key: str, value: Any) -> tuple[str, Any] | None:
        if not key.startswith(self.prefix):
            return key, value
        new_key = f"{self.rewrite_to}{key[len(self.prefix) :]}"
        if self.deprecation:
            msg = f"`{key}` is deprecated and must be renamed to `{new_key}`"
            warnings.warn(msg, self.deprecation)
        return new_key, value

    def reverse_rewrite(self, key: str) -> str | None:
        if key.startswith(self.rewrite_to):
            return f"{self.prefix}{key[len(self.rewrite_to) :]}"
        return None


class ValueRewrite(BaseRewrite):
    """
    Map parameter's values according to map.
    """

    def __init__(
        self, key: str, value: str, new_value: str, /, deprecation: type[Warning] | None = None
    ) -> None:
        super().__init__(deprecation=deprecation)
        self.key = key
        self.value = value
        self.new_value = new_value

    def rewrite(self, key: str, value: Any) -> tuple[str, Any] | None:
        if key != self.key or self.value != str(value):
            return key, value
        if self.deprecation:
            msg = f"{key} = {value} is deprecated, use {self.new_value} instead"
            warnings.warn(msg, self.deprecation)
        return self.key, self.new_value


class DeprecatedValue(BaseRewrite):
    def __init__(self, key: str, value: str, /, deprecation: type[Warning] | None = None) -> None:
        super().__init__(deprecation=deprecation)
        self.key = key
        self.value = value

    def rewrite(self, key: str, value: Any) -> tuple[str, Any] | None:
        if key == self.key and self.value == str(value) and self.deprecation:
            msg = f"{key} = {value} is deprecated and will be removed"
            warnings.warn(msg, self.deprecation)
        return key, value


class ConfigBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._params = {}
        for k in attrs:
            if isinstance(attrs[k], BaseParameter):
                cls._params[k] = attrs[k]
                cls._params[k].name = k
            elif inspect.isclass(attrs[k]) and issubclass(attrs[k], ConfigSection):
                for kk in attrs[k]._params:
                    cls._params[f"{k}.{kk}"] = attrs[k]._params[kk]
        return cls


class BaseConfig(metaclass=ConfigBase):
    PROTOCOLS = {
        "consul": "noc.core.config.proto.consul.ConsulProtocol",
        "env": "noc.core.config.proto.env.EnvProtocol",
        "yaml": "noc.core.config.proto.yaml.YAMLProtocol",
        "legacy": "noc.core.config.proto.legacy.LegacyProtocol",
    }

    _rx_env_sh = re.compile(r"\${([^:}]+)(:-[^}]+)?}")
    _params: dict[str, BaseParameter]

    def __init__(self, rewrites: Iterable[BaseRewrite] | None = None) -> None:
        self._rewrites = list(rewrites) if rewrites else None
        self._params_order = sorted(self._params, key=lambda x: self._params[x].param_number)
        self._rewritten_params = self._get_rewritten_params()

    def __iter__(self):
        yield from self._params_order
        if self._rewritten_params:
            yield from self._rewritten_params

    def _get_rewritten_params(self) -> list[str] | None:
        """Find rewritten params, if any."""
        if not self._rewrites:
            return None
        r: set[str] = set()
        for rule in self._rewrites:
            for p in self._params_order:
                old = rule.reverse_rewrite(p)
                if old:
                    r.add(old)
        return sorted(r) if r else None

    @classmethod
    def expand(cls, value):
        def env_repl(match):
            name, default = match.groups()
            if default is None:
                default = ""
            ev = os.environ.get(name)
            return default if ev is None else ev

        if value.startswith("_env:"):
            # Perform registry like environment expansion
            # _env:VAR, _env:VAR:default
            parts = value[5:].split(":", 1)
            name = parts[0]
            if len(parts) == 1:
                default = ""
            else:
                default = parts[1]
            value = os.environ.get(name)
            if value is None:
                value = default
            return value
        # Perform shell-style environment expansion
        # ${VAR}, ${VAR:-default}
        return cls._rx_env_sh.sub(env_repl, value)

    def set_parameter(self, path, value):
        if value is None:
            return
        if isinstance(value, str):
            value = self.expand(value)
        r = self.rewrite(path, value)
        if r is None:
            return
        path, value = r
        p = self._params.get(path)
        if p is None:
            msg = f"Unknown parameter: {path}"
            raise ConfigurationError(msg)
        p.set_value(value)

    def rewrite(self, key: str, value: Any) -> tuple[str, Any] | None:
        """
        Rewrite parameters.

        Args:
            key: dot-separated parameter's path.
            value: parameter's value.

        Returns:
            (key, value): Rewritten parameters.
            None: Parameter should be dropped.
        """
        if self._rewrites:
            for rule in self._rewrites:
                r = rule.rewrite(key, value)
                if r is None:
                    return None
                key, value = r
        return key, value

    def find_parameter(self, path) -> BaseParameter:
        """
        Get parameter instance by name.

        Args:
            path: Comma-separated path

        Returns:
            Parameter instance
        """
        return self._params[path]

    def get_parameter(self, path):
        return self._params[path].value

    def dump_parameter(self, path):
        if self._rewritten_params and path in self._rewritten_params:
            return None
        return self._params[path].dump_value()

    @classmethod
    def get_protocol(cls, url):
        p = url.split(":", 1)[0]
        h = cls.PROTOCOLS.get(p)
        if h:
            # NB: We cannot use get_handler, so use naive implementation
            module_name, handler_class = h.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, handler_class)
        msg = f"Invalid protocol: {p}"
        raise ValueError(msg)

    def load(self):
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            paths = os.environ.get("NOC_CONFIG", DEFAULT_CONFIG)
            for p in paths.split(","):
                p = p.strip()
                pcls = self.get_protocol(p)
                proto = pcls(self, p)
                proto.load()

    def dump(self, url=DEFAULT_DUMP_URL, section=None):
        pcls = self.get_protocol(url)
        proto = pcls(self, url)
        proto.dump(section=section)

    def update(self, cfg):
        """
        Update config from dictionary
        :return:
        """
        assert isinstance(cfg, dict)
        for name in self:
            c = cfg
            parts = name.split(".")
            for n in parts[:-1]:
                if n in c and isinstance(c[n], dict):
                    c = c[n]
                else:
                    c = None
                    break
            if c and parts[-1] in c:
                self.set_parameter(name, c[parts[-1]])

    def iter_params(self) -> Iterable[tuple[str, BaseParameter]]:
        """
        Iterate over all known parameters.

        Returns:
            Yields of tuples of (parameter name, `BaseParameter instance)
        """
        yield from self._params.items()
