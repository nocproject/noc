# ----------------------------------------------------------------------
# Configuration class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect
import re
import os
from typing import Any, cast
from collections.abc import Iterable
import warnings

# NOC modules
from noc.core.typing import SENTINEL
from .params import BaseParameter
from .backends.base import from_url, BaseConfigBackend


class ConfigurationError(Exception):
    """Configuration error."""


class ConfigSectionBase(type):
    """Metaclass for collecting configuration section parameters."""

    def __new__(
        mcs: "type[ConfigSectionBase]",
        name: str,
        bases: tuple[type[Any], ...],
        attrs: dict[str, Any],
    ) -> type["ConfigSection"]:
        """Create configuration section class and collect parameters.

        Args:
            name: Class name.
            bases: Base classes.
            attrs: Class attributes.

        Returns:
            Created configuration section class.
        """
        cls = cast(type["ConfigSection"], type.__new__(mcs, name, bases, attrs))
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
    """Base class for nested configuration sections."""


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
    """Metaclass for collecting configuration parameters."""

    def __new__(
        mcs: "type[ConfigBase]",
        name: str,
        bases: tuple[type[Any], ...],
        attrs: dict[str, Any],
    ) -> type["BaseConfig"]:
        """Create configuration class and collect parameters.

        Args:
            name: Class name.
            bases: Base classes.
            attrs: Class attributes.

        Returns:
            Created configuration class.
        """
        cls = cast(type["BaseConfig"], type.__new__(mcs, name, bases, attrs))
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
    """Base configuration class.

    Provides parameter discovery, loading from configuration backends,
    parameter rewriting and serialization support.

    Args:
        rewrites: Optional parameter rewrite rules.
    """

    _rx_env_sh = re.compile(r"\${([^:}]+)(:-[^}]+)?}")
    _params: dict[str, BaseParameter]

    def __init__(self, rewrites: Iterable[BaseRewrite] | None = None) -> None:
        self._rewrites = list(rewrites) if rewrites else None
        self._params_order = sorted(self._params, key=lambda x: self._params[x].param_number)
        self._rewritten_params = self._get_rewritten_params()

    def __iter__(self):
        """Iterate over known configuration parameter names.

        Yields:
            Configuration parameter names.
        """
        yield from self._params_order
        if self._rewritten_params:
            yield from self._rewritten_params

    def _get_rewritten_params(self) -> list[str] | None:
        """Find parameter names available through rewrite rules.

        Returns:
            List of rewritten parameter names or None when no rewrite rules
            are configured.
        """
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
        """Expand environment variables in configuration value.

        Supports shell-style expansion::

            ${VAR}
            ${VAR:-default}

        and registry-style expansion::

            _env:VAR
            _env:VAR:default

        Args:
            value: Value to expand.

        Returns:
            Expanded value.
        """

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
        """Set configuration parameter value.

        The value is expanded, rewritten and validated before being assigned.

        Args:
            path: Dot-separated parameter name.
            value: Parameter value.

        Raises:
            ConfigurationError: If parameter is unknown.
        """
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

    def find_parameter(self, path: str) -> BaseParameter:
        """
        Get parameter instance by name.

        Args:
            path: Comma-separated path

        Returns:
            Parameter instance
        """
        return self._params[path]

    def get_parameter(self, path: str):
        """Get current parameter value.

        Args:
            path: Parameter name.

        Returns:
            Current parameter value.
        """
        return self._params[path].value

    def dump_parameter(self, path: str):
        """Serialize parameter value.

        Rewritten aliases are not dumped to avoid duplicate output.

        Args:
            path: Parameter name.

        Returns:
            Serialized parameter value or None when parameter is hidden.
        """
        if self._rewritten_params and path in self._rewritten_params:
            return None
        return self._params[path].dump_value()

    @classmethod
    def get_backend(cls, url: str) -> BaseConfigBackend:
        """Create configuration backend from URL.

        Args:
            url: Backend URL.

        Returns:
            Initialized configuration backend.
        """
        return from_url(url)

    def load(self, cfg: str) -> None:
        """Load configuration values from backends.

        Multiple backends can be specified as comma-separated URLs.
        Values from later backends override values from earlier backends.

        Args:
            cfg: Comma-separated backend URLs.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            backends = [self.get_backend(p) for p in cfg.split(",")]
            for name in self:
                v = SENTINEL
                for backend in backends:
                    nv = backend.get(name, SENTINEL)
                    if nv is not SENTINEL:
                        v = nv
                if v is not SENTINEL:
                    self.set_parameter(name, v)

    def update(self, cfg) -> None:
        """Update configuration from dictionary.

        Nested dictionaries are resolved using dot-separated parameter names.

        Args:
            cfg: Configuration mapping.
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
        """Iterate over registered parameters.

        Returns:
            Iterator yielding parameter name and parameter instance pairs.
        """
        yield from self._params.items()
