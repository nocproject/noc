# ----------------------------------------------------------------------
# ConfDB media sources syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from .audio.base import MEDIA_SOURCES_AUDIO_SYNTAX
from .video.base import MEDIA_SOURCES_VIDEO_SYNTAX

MEDIA_SOURCES_SYNTAX = DEF("sources", [MEDIA_SOURCES_VIDEO_SYNTAX, MEDIA_SOURCES_AUDIO_SYNTAX])
