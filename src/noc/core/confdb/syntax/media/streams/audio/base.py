# ----------------------------------------------------------------------
# ConfDB media streams <name> audio syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import BOOL, INTEGER, CHOICES

MEDIA_STREAMS_AUDIO_SYNTAX = DEF(
    "audio",
    [
        DEF(
            "admin-status",
            [
                DEF(
                    BOOL,
                    name="admin_status",
                    required=True,
                    gen="make_media_streams_audio_admin_status",
                )
            ],
        ),
        DEF(
            "codec",
            [
                DEF(
                    CHOICES("g711a", "g711u", "g726", "aac"),
                    name="codec",
                    required=True,
                    gen="make_media_streams_audio_codec",
                )
            ],
        ),
        DEF(
            "bitrate",
            [DEF(INTEGER, name="bitrate", required=False, gen="make_media_streams_audio_bitrate")],
        ),
        DEF(
            "samplerate",
            [
                DEF(
                    INTEGER,
                    name="samplerate",
                    required=False,
                    gen="make_media_streams_audio_samplerate",
                )
            ],
        ),
    ],
)
