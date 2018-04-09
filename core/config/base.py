# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Configuration class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import inspect
import re
import os
# Third-party modules
import six
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
            elif (inspect.isclass(attrs[k]) and issubclass(attrs[k], ConfigSection)):
                for kk in attrs[k]._params:
                    sn = "%s.%s" % (k, kk)
                    cls._params[sn] = attrs[k]._params[kk]
        cls._params_order = sorted(
            cls._params,
            key=lambda x: cls._params[x].param_number
        )
        return cls


class BaseConfig(six.with_metaclass(ConfigBase)):
    PROTOCOLS = {
        "consul": "noc.core.config.proto.consul.ConsulProtocol",
        "env": "noc.core.config.proto.env.EnvProtocol",
        "yaml": "noc.core.config.proto.yaml.YAMLProtocol",
        "legacy": "noc.core.config.proto.legacy.LegacyProtocol"
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
        if value is None:
            return
        if isinstance(value, six.string_types):
            value = self.expand(value)
        self._params[path].set_value(value)

    def get_parameter(self, path):
        return self._params[path].value

    def dump_parameter(self, path):
        return self._params[path].dump_value()

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
        paths = os.environ.get("NOC_CONFIG", DEFAULT_CONFIG)
        for p in paths.split(","):
            p = p.strip()
            pcls = self.get_protocol(p)
            proto = pcls(self, p)
            proto.load()

    def dump(self, url=DEFAULT_DUMP_URL):
        pcls = self.get_protocol(url)
        proto = pcls(self, url)
        proto.dump()

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
