# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Interface base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import six
# NOC modules
from .error import InterfaceTypeError
from noc.core.interface.parameter import BaseParameter as Parameter

RESERVED_NAMES = {"returns", "template", "form", "preview"}


class BaseInterfaceMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        for k in attrs:
            if k in RESERVED_NAMES:
                continue
            if issubclass(attrs[k].__class__, Parameter):
                p = attrs[k]
                n._INPUT_PARAMS += [(k, p)]
                n._INPUT_MAP[k] = p
                if p.required and p.default is not None:
                    n._INPUT_DEFAULTS[k] = p.default
                if p.required:
                    n._REQUIRED_INPUT.add(k)
        return n


class BaseInterface(six.with_metaclass(BaseInterfaceMetaclass, object)):
    template = None  # Relative template path in sa/templates/
    form = None
    preview = None
    _INPUT_PARAMS = []  # Populated by metaclass
    _INPUT_MAP = {}  # name -> parameter, Populated by metaclass
    _INPUT_DEFAULTS = {}  # name -> default, populated by metaclass
    _REQUIRED_INPUT = set()  # name of required input params

    def gen_parameters(self):
        """
        Generator yielding (parameter name, parameter instance) pairs
        """
        return self._INPUT_PARAMS

    @property
    def has_required_params(self):
        return any(p for n, p in self.gen_parameters() if p.required)

    def clean(self, __profile=None, **kwargs):
        """
        Clean up all parameters except "returns"
        """
        out = self._INPUT_DEFAULTS.copy()
        for k in kwargs:
            param = self._INPUT_MAP.get(k)
            if param:
                value = kwargs[k]
                # Skip Nones
                if value is None:
                    continue
                # Clean parameter
                try:
                    if __profile:
                        out[k] = param.script_clean_input(__profile, value)
                    else:
                        out[k] = param.clean(value)
                except InterfaceTypeError as e:
                    raise InterfaceTypeError("Invalid value for '%s': %s" % (k, e))
            elif k != "__profile":
                # Not found, pass as-is
                out[k] = kwargs[k]
        # Check all required parameters present
        missed = self._REQUIRED_INPUT - set(out)
        if missed:
            raise InterfaceTypeError("Parameter '%s' required" % missed.pop())
        return out

    def clean_result(self, result):
        """
        Clean up returned result
        """
        rp = getattr(self, "returns", None)
        if rp:
            return rp.clean(result)
        return result

    def script_clean_input(self, __profile, **kwargs):
        return self.clean(__profile, **kwargs)

    def script_clean_result(self, __profile, result):
        rp = getattr(self, "returns", None)
        if rp:
            return rp.script_clean_result(__profile, result)
        return result

    def template_clean_result(self, __profile, result):
        return result

    def requires_input(self):
        for n, p in self.gen_parameters():
            return True
        return False

    def get_form(self):
        if self.form:
            return self.form
        r = []
        for n, p in self.gen_parameters():
            r += [p.get_form_field(n)]
        return r
