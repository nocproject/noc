# ----------------------------------------------------------------------
# Syntax Definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Union, Optional, List
from xmlrpc.client import boolean

# NOC modules
from .patterns import BasePattern


@dataclass
class SyntaxDef(object):
    __slots__ = ("children", "default", "gen", "multi", "name", "required", "token")
    token: Union[str, BasePattern]
    children: Optional[List["SyntaxDef"]]
    required: boolean
    name: Optional[str]
    multi: boolean
    default: Optional[str]
    gen: Optional[str]


def DEF(
    token: Union[str, BasePattern],
    children: Optional[List[SyntaxDef]] = None,
    required: boolean = False,
    multi: boolean = False,
    name: Optional[str] = None,
    default: Optional[str] = None,
    gen: Optional[str] = None,
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
