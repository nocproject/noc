# ----------------------------------------------------------------------
# Message class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass


@dataclass
class Message:
    value: bytes
    subject: str
    offset: int
    timestamp: int
    key: bytes
    partition: int
    headers: dict[str, bytes]


@dataclass
class PublishRequest:
    __slots__ = ("data", "headers", "key", "partition", "stream")

    stream: str
    data: bytes
    partition: int | None
    headers: dict[str, bytes] | None
    # Meta
    key: bytes | None
