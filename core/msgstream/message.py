# ----------------------------------------------------------------------
# Message class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Message(object):
    value: bytes
    subject: str
    offset: int
    timestamp: int
    key: bytes
    partition: int
    headers: Dict[str, bytes]


@dataclass
class PublishRequest(object):
    __slots__ = ("data", "headers", "key", "partition", "stream")

    stream: str
    data: bytes
    partition: Optional[int]
    headers: Optional[Dict[str, bytes]]
    # Meta
    key: Optional[bytes]
