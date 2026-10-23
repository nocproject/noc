# ----------------------------------------------------------------------
# Syntax Definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from xmlrpc.client import boolean

# NOC modules
from .patterns import BasePattern


@dataclass
class SyntaxDef:
    __slots__ = ("children", "default", "gen", "multi", "name", "required", "token")
    token: str | BasePattern
    children: list["SyntaxDef"] | None
    required: boolean
    name: str | None
    multi: boolean
    default: str | None
    gen: str | None


def DEF(
    token: str | BasePattern,
    children: list[SyntaxDef] | None = None,
    required: boolean = False,
    multi: boolean = False,
    name: str | None = None,
    default: str | None = None,
    gen: str | None = None,
) -> SyntaxDef:
    return SyntaxDef(
        token=token,
        children=children,
        required=required,
        name=name,
        multi=multi,
        default=default,
        gen=gen,
    )
