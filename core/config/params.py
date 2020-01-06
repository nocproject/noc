# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Config parameters
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import logging

# Third-party modules
import six

# NOC modules
from noc.core.validators import is_int, is_ipv4
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


class BaseParameter(object):
    PARAM_NUMBER = itertools.count()

    def __init__(self, default=None, help=None):
        self.param_number = next(self.PARAM_NUMBER)
        if default is None:
            self.default = None
            self.orig_value = None
        else:
            self.orig_value = default
            self.default = self.clean(default)
        self.help = help
        self.name = None  # Set by metaclass
        self.value = self.default  # Set by __set__ method

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.set_value(value)

    def set_value(self, value):
        self.orig_value = value
        self.value = self.clean(value)

    def clean(self, v):
        return v

    def dump_value(self):
        return self.value


class StringParameter(BaseParameter):
    def __init__(self, default=None, help=None, choices=None):
        self.choices = choices
        super(StringParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        v = smart_text(v)
        if self.choices:
            if v not in self.choices:
                raise ValueError("Invalid value: %s" % v)
        return v


class SecretParameter(BaseParameter):
    def __init__(self, default=None, help=None, choices=None):
        super(SecretParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        return smart_text(v)

    def __repr__(self):
        return "****hidden****"


class IntParameter(BaseParameter):
    def __init__(self, default=None, help=None, min=None, max=None):
        self.min = min
        self.max = max
        super(IntParameter, self).__init__(default=default, help=None)

    def clean(self, v):
        v = int(v)
        if self.min is not None:
            if v < self.min:
                raise ValueError("Value is less than %d" % self.min)
        if self.max is not None:
            if v > self.max:
                raise ValueError("Value is greater than %d" % self.max)
        return v


class BooleanParameter(BaseParameter):
    def clean(self, v):
        if isinstance(v, six.string_types):
            v = v.lower() in ["y", "t", "true", "yes"]
        return bool(v)


class FloatParameter(BaseParameter):
    def clean(self, v):
        return float(v)


class MapParameter(BaseParameter):
    def __init__(self, default=None, help=None, mappings=None):
        self.mappings = mappings or {}
        super(MapParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        try:
            return self.mappings[smart_text(v)]
        except KeyError:
            raise ValueError("Invalid value %s" % v)

    def dump_value(self):
        if not self.mappings:
            return super(MapParameter, self).dump_value()
        for mv in self.mappings:
            if self.mappings[mv] == self.value:
                return mv
        return self.value


class HandlerParameter(BaseParameter):
    def clean(self, v):
        # h = get_handler(v)
        # if not h:
        #     raise ValueError("Invalid handler: %s" % v)
        # return h
        return v


class SecondsParameter(BaseParameter):
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

    def clean(self, v):
        if isinstance(v, six.integer_types):
            return v
        m = self.SCALE.get(v[-1], None)
        if m is None:
            m = 1
        else:
            v = v[:-1]
        try:
            v = int(v)
        except ValueError:
            raise ValueError("Invalid value: %s" % v)
        return v * m

    def dump_value(self):
        if not self.value > 0:
            return 0
        for d, s in self.SHORT_FORM:
            n, r = divmod(self.value, d)
            if not r:
                return "%d%s" % (n, s)
        return "%ss" % self.value


class ListParameter(BaseParameter):
    def __init__(self, default=None, help=None, item=None):
        self.item = item
        super(ListParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        return [self.item.clean(x) for x in v]


class ServiceItem(object):
    __slots__ = ["host", "port"]

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __str__(self):
        return "%s:%s" % (self.host, self.port)

    def __repr__(self):
        return "<ServiceItem %s:%s>" % (self.host, self.port)

    def __contains__(self, item):
        return item in "%s:%s" % (self.host, self.port)


class ServiceParameter(BaseParameter):
    """
    Resolve external service location to a list of ServiceItem.
    Service resolved at startup,
    though in future implementation it can be changed during runtime

    Resolves to empty list when service is not available
    :param service: Service name
    :param near: Resolve to nearest service
    :param wait: Block and wait until at least one instance of
       service will be available
    """

    DEFAULT_RESOLUTION_TIMEOUT = 1

    def __init__(self, service, near=False, wait=True, help=None, full_result=True, critical=True):
        if isinstance(service, six.string_types):
            self.services = [service]
        else:
            self.services = service
        self.near = near
        self.wait = wait
        self.full_result = full_result
        self.critical = critical
        super(ServiceParameter, self).__init__(default=[], help=help)

    def __get__(self, instance, owner):
        if not self.value:
            self.resolve()
        return self.value

    def set_value(self, value):
        self.value = None
        value = smart_text(value)
        if isinstance(value, six.string_types):
            self.services = [value]
        else:
            self.services = value

    def resolve(self):
        from noc.core.dcs.util import resolve
        from noc.core.dcs.error import ResolutionError

        if isinstance(self.services, list) and ":" in self.services[0]:
            self.value = [ServiceItem(*i.rsplit(":", 1)) for i in self.services]
            return
        elif isinstance(self.services, six.string_types) and ":" in self.services:
            self.value = self.services
            return

        while True:
            for svc in self.services:
                if ServiceParameter.is_static(svc):
                    self.value = [ServiceItem(*svc.split(":"))]
                    break
                try:
                    items = resolve(
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

    def as_list(self):
        """
        :return: List of <host>:<port>
        """
        return [str(i) for i in self.value]

    def dump_value(self):
        if len(self.services) == 1:
            return self.services[0]
        else:
            return self.services

    @staticmethod
    def is_static(svc):
        if ":" not in svc:
            return False
        p = svc.split(":")
        if len(p) != 2:
            return False
        return is_ipv4(p[0]) and is_int(p[1])
