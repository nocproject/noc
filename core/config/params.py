# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Config parameters
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
# Third-party modules
import six


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
        self.orig_value = value
        self.value = self.clean(value)

    def clean(self, v):
        return v


class StringParameter(BaseParameter):
    def __init__(self, default=None, help=None, choices=None):
        self.choices = choices
        super(StringParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        v = str(v)
        if self.choices:
            if v not in self.choices:
                raise ValueError("Invalid value: %s" % v)
        return v


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
        return v


class FloatParameter(BaseParameter):
    def clean(self, v):
        return float(v)


class MapParameter(BaseParameter):
    def __init__(self, default=None, help=None, mappings=None):
        self.mappings = mappings or {}
        super(MapParameter, self).__init__(default=default, help=help)

    def clean(self, v):
        try:
            return self.mappings[v]
        except KeyError:
            raise ValueError("Invalid value %s" % v)


class HandlerParameter(BaseParameter):
    def clean(self, v):
        # h = get_handler(v)
        # if not h:
        #     raise ValueError("Invalid handler: %s" % v)
        # return h
        return v


class SecondsParameter(BaseParameter):
    def clean(self, v):
        m = 1
        if v.endswith("h"):
            v = v[:-1]
            m = 3600
        elif v.endswith("d"):
            v = v[:-1]
            m = 24 * 3600
        elif v.endswith("w"):
            v = v[:-1]
            m = 7 * 24 * 3600
        elif v.endswith("m"):
            v = v[:-1]
            m = 30 * 24 * 3600
        elif v.endswith("y"):
            v = v[:-1]
            m = 365 * 24 * 3600
        try:
            v = int(v)
        except ValueError:
            raise ValueError("Invalid value: %s" % v)
        return v * m


class ListParameter(BaseParameter):
    def __init__(self, default=None, help=None, lists=None):
        self.list = lists or []
        super(ListParameter, self).__init__(default=default, help=help)
        # @todo add clean method
