# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB patterns
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six


class BasePattern(object):
    # __slots__ = ["match_rest"] conflicts with py3
    match_rest = False

    def match(self, token):
        raise NotImplementedError

    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return "%s=None" % name
        return "%s='%s'" % (name, value.replace("'", "\\'"))

    @staticmethod
    def compile_value(name):
        return name


class ANY(BasePattern):
    @staticmethod
    def match(token):
        return True

    def __repr__(self):
        return "ANY"


class REST(BasePattern):
    match_rest = True

    @staticmethod
    def match(token):
        return True

    def __repr__(self):
        return "REST"


class Token(BasePattern):
    def __init__(self, token):
        super(Token, self).__init__()
        self.token = token

    def match(self, token):
        return token == self.token

    def __repr__(self):
        return repr(self.token)


class BOOL(ANY):
    @staticmethod
    def clean(value):
        if isinstance(value, six.string_types):
            return value.lower() in ("true", "on", "yes")
        return bool(value)

    @staticmethod
    def compile_gen_kwarg(name, value=None):
        return "%s=%s" % (name, BOOL.clean(value))

    @staticmethod
    def compile_value(name):
        return "BOOL.clean(%s)" % name


class INTEGER(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return "%s=None" % name
        return "%s=%s" % (name, int(value))

    @staticmethod
    def compile_value(name):
        return "int(%s)" % name


class FLOAT(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return "%s=None" % name
        return "%s=%s" % (name, float(value))

    @staticmethod
    def compile_value(name):
        return "float(%s)" % name


# Matches any token value
VR_NAME = ANY
FI_NAME = ANY
IF_NAME = ANY
UNIT_NAME = ANY
IF_UNIT_NAME = ANY
IPv4_ADDRESS = ANY
IPv4_PREFIX = ANY
IPv6_ADDRESS = ANY
IPv6_PREFIX = ANY
IP_ADDRESS = ANY
ISO_ADDRESS = ANY
# INTEGER = ANY
# FLOAT = ANY
# BOOL = ANY
ETHER_MODE = ANY
STP_MODE = ANY
HHMM = ANY


def CHOICES(*args):
    return ANY
