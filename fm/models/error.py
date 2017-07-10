# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class MIBRequiredException(Exception):
    def __init__(self, mib, requires_mib):
        super(MIBRequiredException, self).__init__()
        self.mib = mib
        self.requires_mib = requires_mib

    def __str__(self):
        return "%s requires %s" % (self.mib, self.requires_mib)


class MIBNotFoundException(Exception):
    def __init__(self, mib):
        super(MIBNotFoundException, self).__init__()
        self.mib = mib

    def __str__(self):
        return "MIB not found: %s" % self.mib


class InvalidTypedef(Exception):
    pass


class OIDCollision(Exception):
    def __init__(self, oid, name1, name2, msg=None):
        self.oid = oid
        self.name1 = name1
        self.name2 = name2
        self.msg = msg

    def __str__(self):
        s = "Cannot resolve OID %s collision between %s and %s" % (
            self.oid, self.name1, self.name2)
        if self.msg:
            s += ". %s" % self.msg
        return s
