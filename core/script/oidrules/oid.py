# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OIDRule base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import sys
# Third-party modules
import six
# NOC modules
from noc.core.mib import mib

rx_rule_var = re.compile(r"{{\s*([^}]+?)\s*}}")


class OIDRule(object):
    """
    SNMP OID generator for SNMP_OIDS
    """
    name = "oid"
    default_type = "gauge"

    _scale_locals = {}

    def __init__(self, oid, type=None, scale=1, path=None):
        self.oid = oid
        self.is_complex = not isinstance(oid, six.string_types)
        self.type = type or self.default_type
        self.scale = self._convert_scale(scale)
        self.path = path or []

    def _convert_scale(self, scale):
        """
        Convert scale expression to callable or constant
        :param scale:
        :return:
        """
        if isinstance(scale, six.string_types):
            return eval(scale, self._scale_locals)
        return scale

    def iter_oids(self, script, metric):
        """
        Generator yielding oid, type, scale, path
        :param script:
        :param metric:
        :return:
        """
        if self.is_complex:
            yield tuple(self.oid), self.type, self.scale, self.path
        else:
            yield self.oid, self.type, self.scale, self.path

    @classmethod
    def from_json(cls, data):
        kwargs = {}
        for k in data:
            if not k.startswith("$"):
                kwargs[k] = data[k]
        return cls(**kwargs)

    @classmethod
    def expand(cls, template, context):
        """
        Expand {{ var }} expressions in template with given context
        :param template:
        :param context:
        :return:
        """
        return rx_rule_var.sub(
            lambda x: str(context[x.group(1)]),
            template
        )

    def expand_oid(self, **kwargs):
        """
        Apply kwargs to template and return resulting oid
        :param kwargs:
        :return:
        """
        if self.is_complex:
            oids = tuple(mib[self.expand(o, kwargs)] for o in self.oid)
            if None in oids:
                return None
            else:
                return oids
        else:
            return mib[self.expand(self.oid, kwargs)]

    @classmethod
    def _build_scale_locals(cls):
        """
        Build locals for scale evaluation
        :return:
        """
        import noc.core.script.metrics  # noqa
        m = sys.modules["noc.core.script.metrics"]
        lv = {}
        for n in dir(m):
            if not n.startswith("_"):
                lv[n] = getattr(m, n)
        cls._scale_locals = lv


# Build scale local context
OIDRule._build_scale_locals()
