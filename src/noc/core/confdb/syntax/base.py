# ----------------------------------------------------------------------
# ConfDB Syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from .hints import HINTS_SYNTAX
from .interfaces.base import INTERFACES_SYNTAX
from .media.base import MEDIA_SYNTAX
from .meta.base import META_SYNTAX
from .protocols.base import PROTOCOLS_SYNTAX
from .system.base import SYSTEM_SYNTAX
from .virtualrouter.base import VIRTUAL_ROUTER_SYNTAX

SYNTAX = [
    META_SYNTAX,
    SYSTEM_SYNTAX,
    INTERFACES_SYNTAX,
    PROTOCOLS_SYNTAX,
    VIRTUAL_ROUTER_SYNTAX,
    MEDIA_SYNTAX,
    HINTS_SYNTAX,
]
