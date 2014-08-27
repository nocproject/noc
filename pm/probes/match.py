## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe match expressions
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class MatchExprBase(type):
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        if m.op:
            m.OP_MAP[m.op] = m
        return m


class MatchExpr(object):
    __metaclass__ = MatchExprBase

    op = None

    OP_MAP = {}

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "(%s %s %s)" % (self.name, self.op, self.value)

    @classmethod
    def create(cls, name, op, value):
        return cls.OP_MAP[op](name, value)

    def __and__(self, other):
        return MatchAnd(self, other)

    def __or__(self, other):
        return MatchOr(self, other)

    def get_vars(self):
        """
        Returns tuple of required variables, optional variables
        """
        return set([self.name]), set()

    def compile(self):
        raise NotImplementedError()


class MatchEq(MatchExpr):
    op = "eq"

    def compile(self):
        return lambda config: (self.name in config and
                               config[self.name] == self.value)


class MatchAnd(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "( %r AND %r )" % (self.left, self.right)

    def get_vars(self):
        lr, lo = self.left.get_vars()
        rr, ro = self.right.get_vars()
        r = lr | rr
        o = lo | ro
        o -= r
        return r, o

    def compile(self):
        lv = self.left.compile()
        rv = self.right.compile()
        return lambda config: lv(config) and rv(config)


class MatchOr(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "( %r OR %r )" % (self.left, self.right)

    def get_vars(self):
        lr, lo = self.left.get_vars()
        rr, ro = self.right.get_vars()
        l = lr | lo
        r = rr | ro
        return l & r, l ^ r

    def compile(self):
        lv = self.left.compile()
        rv = self.right.compile()
        return lambda config: lv(config) or rv(config)


class MatchTrue(object):
    def __init__(self):
        pass

    def get_vars(self):
        return set(), set()

    def compile(self):
        return lambda config: True


class MatchFalse(object):
    def __init__(self):
        pass

    def get_vars(self):
        return set(), set()

    def compile(self):
        return lambda config: False