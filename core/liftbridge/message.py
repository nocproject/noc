# ----------------------------------------------------------------------
# Message class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import dataclasses


@dataclasses.dataclass
class Message(object):
    value: bytes
    subject: str
    offset: int
    timestamp: int
    key: bytes
    partition: int
