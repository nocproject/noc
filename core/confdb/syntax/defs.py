# ----------------------------------------------------------------------
# Syntax Definitions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple


SyntaxDef = namedtuple(
    "SyntaxDef", ["token", "children", "required", "name", "multi", "default", "gen"]
)


def DEF(token, children=None, required=False, multi=False, name=None, default=None, gen=None):
    return SyntaxDef(token, children, required, name, multi, default, gen)
