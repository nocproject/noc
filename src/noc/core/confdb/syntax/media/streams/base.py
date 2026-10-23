# ----------------------------------------------------------------------
# ConfDB media streams syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import ANY
from .video.base import MEDIA_STREAMS_VIDEO_SYNTAX
from .audio.base import MEDIA_STREAMS_AUDIO_SYNTAX
from .overlays.base import MEDIA_STREAMS_OVERLAYS_SYNTAX

MEDIA_STREAMS_SYNTAX = DEF(
    "streams",
    [
        DEF(
            ANY,
            [
                DEF(
                    "rtsp-path", [DEF(ANY, name="path", required=True, gen="make_stream_rtsp_path")]
                ),
                DEF(
                    "settings",
                    [
                        MEDIA_STREAMS_VIDEO_SYNTAX,
                        MEDIA_STREAMS_AUDIO_SYNTAX,
                        MEDIA_STREAMS_OVERLAYS_SYNTAX,
                    ],
                ),
            ],
            name="name",
            multi=True,
        )
    ],
)
