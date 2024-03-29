# ----------------------------------------------------------------------
# SNMP Error Codes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum

# No error occurred. This code is also used in all request PDUs,
# since they have no error status to report.
NO_ERROR = 0
# The size of the Response-PDU would be too large to transport.
TOO_BIG = 1
# The name of a requested object was not found.
NO_SUCH_NAME = 2
# A value in the request didn't match the structure that
# the recipient of the request had for the object.
# For example, an object in the request was specified
# with an incorrect length or type.
BAD_VALUE = 3
# An attempt was made to set a variable that has an
# Access value indicating that it is read-only.
READ_ONLY = 4
# An error occurred other than one indicated by
# a more specific error code in this table.
GEN_ERR = 5
# Access was denied to the object for security reasons.
NO_ACCESS = 6
# The object type in a variable binding is incorrect for the object.
WRONG_TYPE = 7
# A variable binding specifies a length incorrect for the object.
WRONG_LENGTH = 8
# A variable binding specifies an encoding incorrect for the object.
WRONG_ENCODING = 9
# The value given in a variable binding is not possible for the object.
WRONG_VALUE = 10
# A specified variable does not exist and cannot be created.
NO_CREATION = 11
# A variable binding specifies a value that could be held
# by the variable but cannot be assigned to it at this time.
INCONSISTENT_VALUE = 12
# An attempt to set a variable required
# a resource that is not available.
RESOURCE_UNAVAILABLE = 13
# An attempt to set a particular variable failed.
COMMIT_FAILED = 14
# An attempt to set a particular variable as part of
# a group of variables failed, and the attempt to then
# undo the setting of other variables was not successful.
UNDO_FAILED = 15
# A problem occurred in authorization.
AUTHORIZATION_ERROR = 16
# The variable cannot be written or created.
NOT_WRITABLE = 17
# The name in a variable binding specifies
# a variable that does not exist.
INCONSISTENT_NAME = 18

# Virtual code
TIMED_OUT = -1
UNREACHABLE = -2
BER_ERROR = -3
BAD_COMMUNITY = -4
END_OID_TREE = -5


class SNMPErrorCode(enum.Enum):
    NO_ERROR = 0
    TOO_BIG = 1
    NO_SUCH_NAME = 2
    BAD_VALUE = 3
    READ_ONLY = 4
    GEN_ERR = 5
    NO_ACCESS = 6
    WRONG_TYPE = 7
    WRONG_LENGTH = 8
    WRONG_ENCODING = 9
    WRONG_VALUE = 10
    NO_CREATION = 11
    INCONSISTENT_VALUE = 12
    RESOURCE_UNAVAILABLE = 13
    COMMIT_FAILED = 14
    UNDO_FAILED = 15
    AUTHORIZATION_ERROR = 16
    NOT_WRITABLE = 17
    INCONSISTENT_NAME = 18
    TIMED_OUT = -1
    UNREACHABLE = -2
    BER_ERROR = -3
    BAD_COMMUNITY = -4
    END_OID_TREE = -5


class SNMPError(Exception):
    def __init__(self, code, oid=None):
        super().__init__()
        self.code = code
        self.oid = oid

    def __repr__(self):
        try:
            name = SNMPErrorCode(self.code).name
        except ValueError:
            name = "UNKNOWN"
        return f"<SNMPError code={self.code}({name}) oid={self.oid}>"
