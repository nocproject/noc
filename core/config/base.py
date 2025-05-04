# ----------------------------------------------------------------------
# Configuration class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect
import re
import os
from typing import Dict, Iterable, Tuple

# NOC modules
from .params import BaseParameter

DEFAULT_CONFIG = "yaml:///opt/noc/etc/tower.yml,yaml:///opt/noc/etc/settings.yml,env:///NOC"
DEFAULT_DUMP_URL = "yaml://"


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


class ConfigSection(object, metaclass=ConfigSectionBase):
    pass


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
        cls._params_order = sorted(cls._params, key=lambda x: cls._params[x].param_number)
        return cls


class BaseConfig(object, metaclass=ConfigBase):
    PROTOCOLS = {
        "consul": "noc.core.config.proto.consul.ConsulProtocol",
        "env": "noc.core.config.proto.env.EnvProtocol",
        "yaml": "noc.core.config.proto.yaml.YAMLProtocol",
        "legacy": "noc.core.config.proto.legacy.LegacyProtocol",
    }

    _rx_env_sh = re.compile(r"\${([^:}]+)(:-[^}]+)?}")
    _params: Dict[str, BaseParameter]

    def __iter__(self):
        yield from self._params_order

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
        self._params[path].set_value(value)

    def find_parameter(self, path) -> BaseParameter:
        """
        Get parameter instance by name
        :param path: Comma-separated path
        :return: Parameter instance
        """
        return self._params[path]

    def get_parameter(self, path):
        return self._params[path].value

    def dump_parameter(self, path):
        return self._params[path].dump_value()

    @classmethod
    def get_protocol(cls, url):
        p = url.split(":", 1)[0]
        h = cls.PROTOCOLS.get(p)
        if h:
            # NB: We cannot use get_handler, so use naive implementation
            module_name, handler_class = h.rsplit(".", 1)
            module = __import__(module_name, {}, {}, [handler_class])
            return getattr(module, handler_class)
        msg = f"Invalid protocol: {p}"
        raise ValueError(msg)

    def load(self):
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
        :param cfg:
        :return:
        """
        assert isinstance(cfg, dict)
        for name in self._params_order:
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

    def iter_params(self) -> Iterable[Tuple[str, BaseParameter]]:
        """
        Iterate over all known parameters.

        Returns:
            Yields of tuples of (parameter name, `BaseParameter instance)
        """
        yield from self._params.items()
