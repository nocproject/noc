# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect
import re
# Third-party modules
import six
## NOC modules
from params import BaseParameter



class ConfigSectionBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._params = {}
        for k in attrs:
            if isinstance(attrs[k], BaseParameter):
                cls._params[k] = attrs[k]
                cls._params[k].name = k
        return cls


class ConfigSection(six.with_metaclass(ConfigSectionBase)):
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
                    sn = "%s.%s" % (k, kk)
                    cls._params[sn] = attrs[k]._params[kk]
        cls._params_order = sorted(cls._params, key=lambda x: cls._params[x].param_number)
        return cls


class BaseConfig(six.with_metaclass(ConfigBase)):
    DEFAULT_CONFIG = "env:///NOC"

    PROTOCOLS = {
        "env": "noc.core.config.proto.env_proto.EnvProtocol",
        "yaml": "noc.core.config.proto.yaml_proto.YAMLProtocol"
    }

    _rx_env_sh = re.compile(r"\${([^:}]+)(:-[^}]+)?}")

    def __iter__(self):
        for k in self._params_order:
            yield k

    @classmethod
    def expand(cls, value):
        def env_repl(match):
            name, default = match.groups()
            if default is None:
                default = ""
            ev = os.environ.get(name)
            if ev is None:
                return default
            else:
                return ev

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
        else:
            # Perform shell-style environment expansion
            # ${VAR}, ${VAR:-default}
            return cls._rx_env_sh.sub(env_repl, value)

    def set_parameter(self, path, value):
        if isinstance(value, six.string_types):
            value = self.expand(value)
        c = self
        parts = path.split(".")
        for n in parts[:-1]:
            c = getattr(c, n)
        setattr(c, parts[-1], value)

    def get_parameter(self, path):
        v = self._params[path].orig_value
        if v is not None:
            return v
        c = self
        parts = path.split(".")
        for n in parts[:-1]:
            c = getattr(c, n)
        return getattr(c, parts[-1])

    @classmethod
    def get_protocol(cls, url):
        p = url.split(":", 1)[0]
        h = cls.PROTOCOLS.get(p)
        if h:
            from noc.core.handler import get_handler
            return get_handler(h)
        else:
            raise ValueError("Invalid protocol %s" % p)

    def load(self):
        paths = os.environ.get("NOC_CONFIG", self.DEFAULT_CONFIG)
        for p in paths.split(","):
            p = p.strip()
            pcls = self.get_protocol(p)
            proto = pcls(self, p)
            proto.load()

    def dump(self, url=DEFAULT_CONFIG):
        pcls = self.get_protocol(url)
        proto = pcls(self, url)
        proto.dump()
