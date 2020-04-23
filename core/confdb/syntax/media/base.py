# ----------------------------------------------------------------------
# ConfDB media syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from .sources.base import MEDIA_SOURCES_SYNTAX
from .streams.base import MEDIA_STREAMS_SYNTAX

MEDIA_SYNTAX = DEF("media", [MEDIA_SOURCES_SYNTAX, MEDIA_STREAMS_SYNTAX])
