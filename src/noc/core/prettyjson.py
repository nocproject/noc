# ---------------------------------------------------------------------
# Pretty JSON formatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import annotations

import uuid
from collections.abc import Collection

# NOC modules
from noc.core.escape import json_escape
from noc.core.text import indent


def _convert(
    value: object,
    level: int,
    order: Collection[str] | None,
) -> str:
    """
    Convert a Python object to a pretty-printed JSON fragment.

    Args:
        value: Value to serialize.
        level: Current indentation level.
        order: Optional preferred ordering for dictionary keys.

    Returns:
        Pretty-printed JSON fragment.
    """
    match value:
        case None:
            return indent("null", level)
        case str():
            return indent(f'"{json_escape(value)}"', level)
        case bool():
            return indent("true" if value else "false", level)
        case int() | float():
            return indent(str(value), level)
        case uuid.UUID():
            return indent(f'"{value}"', level)
        case list():
            if not value:
                return indent("[]", level)

            items = [_convert(item, 0, order) for item in value]
            line_length = sum(map(len, items)) + level + (len(items) - 1) * 2

            if line_length > 72:
                body = ",\n".join(indent(item, level + 4) for item in items)
                return "\n".join(
                    (
                        indent("[", level),
                        body,
                        indent("]", level),
                    )
                )

            return indent(f"[{', '.join(items)}]", level)
        case dict():
            if not value:
                return indent("{}", level)

            keys = sorted(value)
            if order:
                keys = [k for k in order if k in value] + [k for k in keys if k not in order]

            body = ",\n".join(
                f"{_convert(key, 0, order)}: {_convert(value[key], 0, order)}" for key in keys
            )
            return indent(f"{{\n{indent(body, 4)}\n}}", level)
        case _:
            raise TypeError(f"Cannot encode {type(value).__name__}: {value!r}")


def to_json(
    value: object,
    order: Collection[str] | None = None,
) -> str:
    """
    Serialize an object to pretty-printed JSON.

    Supported types are ``None``, ``str``, ``bool``, ``int``, ``float``,
    ``uuid.UUID``, ``list``, and ``dict``.

    Args:
        value: Value to serialize.
        order: Optional preferred ordering for dictionary keys. Keys not
            listed here are appended in sorted order.

    Returns:
        Pretty-printed JSON terminated by a trailing newline.

    Raises:
        TypeError: If the value contains an unsupported type.
    """
    result = _convert(value, 0, order)
    return result if result.endswith("\n") else f"{result}\n"
