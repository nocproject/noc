# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OIDRule base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# Third-party modules
import six
# NOC modules
from noc.core.mib import mib
from noc.core.handler import get_handler

rx_rule_var = re.compile(r"{{\s*([^}]+?)\s*}}")


class OIDRule(object):
    """
    SNMP OID generator for SNMP_OIDS
    """
    name = "oid"
    default_type = "gauge"

    def __init__(self, oid, type=None, scale=1, path=None):
        self.oid = oid
        self.is_complex = not isinstance(oid, six.string_types)
        self.type = type or self.default_type
        if isinstance(scale, six.string_types):
            self.scale = get_handler(
                "noc.core.script.metrics.%s" % scale
            )
        else:
            self.scale = scale
        self.path = path or []

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