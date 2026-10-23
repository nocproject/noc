# ----------------------------------------------------------------------
# ConfDB patterns
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.ip import IP, IPv4, IPv6


class BasePattern:
    # __slots__ = ["match_rest"] conflicts with py3
    match_rest = False

    def match(self, token):
        raise NotImplementedError

    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return "{}='{}'".format(name, value.replace("'", "\\'"))

    @staticmethod
    def compile_value(name):
        return name


class ANY(BasePattern):
    @staticmethod
    def match(token):
        return True

    def __repr__(self) -> str:
        return "ANY"


class REST(BasePattern):
    match_rest = True

    @staticmethod
    def match(token):
        return True

    def __repr__(self) -> str:
        return "REST"


class Token(BasePattern):
    def __init__(self, token) -> None:
        super().__init__()
        self.token = token

    def match(self, token):
        return token == self.token

    def __repr__(self) -> str:
        return repr(self.token)


class BOOL(ANY):
    @staticmethod
    def clean(value):
        if isinstance(value, str):
            return value.lower() in ("true", "on", "yes")
        return bool(value)

    @staticmethod
    def compile_gen_kwarg(name, value=None):
        return f"{name}={BOOL.clean(value)}"

    @staticmethod
    def compile_value(name):
        return f"BOOL.clean({name})"


class INTEGER(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={int(value)}"

    @staticmethod
    def compile_value(name):
        return f"int({name})"


class FLOAT(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={float(value)}"

    @staticmethod
    def compile_value(name):
        return f"float({name})"


class IP_ADDRESS(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={IP.prefix(value)}"

    @staticmethod
    def compile_value(name):
        return f"IP.prefix({name})"


class IPv4_ADDRESS(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={IPv4(value)}"

    @staticmethod
    def compile_value(name):
        return f"IPv4({name})"


class IPv4_PREFIX(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={IPv4(value)}"

    @staticmethod
    def compile_value(name):
        return f"IPv4({name})"


class IPv6_ADDRESS(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={IPv6(value)}"

    @staticmethod
    def compile_value(name):
        return f"IPv6({name})"


class IPv6_PREFIX(ANY):
    @staticmethod
    def compile_gen_kwarg(name, value=None):
        if value is None:
            return f"{name}=None"
        return f"{name}={IPv6(value)}"

    @staticmethod
    def compile_value(name):
        return f"IPv6({name})"


# Matches any token value
AS_NUM = ANY
VR_NAME = ANY
FI_NAME = ANY
IF_NAME = ANY
UNIT_NAME = ANY
IF_UNIT_NAME = ANY
# IPv4_ADDRESS = ANY
# IPv4_PREFIX = ANY
# IPv6_ADDRESS = ANY
# IPv6_PREFIX = ANY
# IP_ADDRESS = ANY
ISO_ADDRESS = ANY
# INTEGER = ANY
# FLOAT = ANY
# BOOL = ANY
ETHER_MODE = ANY
STP_MODE = ANY
HHMM = ANY


def CHOICES(*args):
    return ANY
