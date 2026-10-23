# ---------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class MIBRequiredException(Exception):
    def __init__(self, mib, requires_mib) -> None:
        super().__init__()
        self.mib = mib
        self.requires_mib = requires_mib

    def __str__(self):
        return f"{self.mib} requires {self.requires_mib}"


class MIBNotFoundException(Exception):
    def __init__(self, mib) -> None:
        super().__init__()
        self.mib = mib

    def __str__(self):
        return f"MIB not found: {self.mib}"


class InvalidTypedef(Exception):
    pass


class OIDCollision(Exception):
    def __init__(self, oid, name1, name2, msg=None) -> None:
        super().__init__()
        self.oid = oid
        self.name1 = name1
        self.name2 = name2
        self.msg = msg

    def __str__(self):
        s = f"Cannot resolve OID {self.oid} collision between {self.name1} and {self.name2}"
        if self.msg:
            s += f". {self.msg}"
        return s
