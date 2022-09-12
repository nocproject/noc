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


@dataclass(frozen=True)
class PublishRequest(object):
    __slots__ = ("stream", "message", "partition", "key", "headers", "auto_compress")
    stream: str
    message: bytes
    partition: int
    key: bytes
    headers: Optional[Dict[str, bytes]]
    auto_compress: bool
