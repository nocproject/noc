# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from error import InterfaceTypeError
from noc.core.interface.parameter import BaseParameter as Parameter


class BaseInterface(object):
    template = None  # Relative template path in sa/templates/
    form = None
    preview = None
    RESERVED_NAMES = ("returns", "template", "form", "preview")

    def gen_parameters(self):
        """
        Generator yielding (parameter name, parameter instance) pairs
        """
        for n, p in self.__class__.__dict__.items():
            if issubclass(p.__class__, Parameter) and n not in self.RESERVED_NAMES:
                yield (n, p)

    @property
    def has_required_params(self):
        return any(p for n, p in self.gen_parameters() if p.required)

    def clean(self, __profile=None, **kwargs):
        """
        Clean up all parameters except "returns"
        """
        in_kwargs = kwargs.copy()
        out_kwargs = {}
        for n, p in self.gen_parameters():
            if n not in in_kwargs and p.required:
                if p.default is not None:
                    out_kwargs[n] = p.default
                else:
                    raise InterfaceTypeError("Parameter '%s' required" % n)
            if n in in_kwargs:
                if not (in_kwargs[n] is None and not p.required):
                    try:
                        if __profile:
                            out_kwargs[n] = p.script_clean_input(__profile,
                                                                 in_kwargs[n])
                        else:
                            out_kwargs[n] = p.clean(in_kwargs[n])
                    except InterfaceTypeError as e:
                        raise InterfaceTypeError("Invalid value for '%s': %s" % (n, e))
                del in_kwargs[n]
        # Copy other parameters
        for k, v in in_kwargs.items():
            if k != "__profile":
                out_kwargs[k] = v
        return out_kwargs

    def clean_result(self, result):
        """
        Clean up returned result
        """
        try:
            rp = self.returns
        except AttributeError:
            return result  # No return result restriction
        return rp.clean(result)

    def script_clean_input(self, __profile, **kwargs):
        return self.clean(__profile, **kwargs)

    def script_clean_result(self, __profile, result):
        try:
            rp = self.returns
        except AttributeError:
            return result
        return rp.script_clean_result(__profile, result)

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
