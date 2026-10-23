# ----------------------------------------------------------------------
# ProtocolConstrain class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseConstraint


class ProtocolConstraint(BaseConstraint):
    """
    Protocol restrictions.

    Represents single protocol.

    Args:
        proto: Protocol name.
    """

    def __init__(self: "ProtocolConstraint", proto: str) -> None:
        super().__init__()
        self._proto = proto

    def __str__(self: "ProtocolConstraint") -> str:
        return self._proto

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ProtocolConstraint) and self._proto == value._proto

    @property
    def protocol(self: "ProtocolConstraint") -> str:
        return self._proto
