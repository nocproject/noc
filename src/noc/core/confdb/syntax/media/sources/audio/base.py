# ----------------------------------------------------------------------
# ConfDB media sources audio syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import ANY, CHOICES, INTEGER, BOOL

MEDIA_SOURCES_AUDIO_SYNTAX = DEF(
    "audio",
    [
        DEF(
            ANY,
            [
                DEF(
                    "source",
                    [
                        DEF(
                            CHOICES("mic", "audio-in"),
                            name="source",
                            required=True,
                            gen="make_audio_source",
                        )
                    ],
                ),
                DEF(
                    "settings",
                    [
                        DEF(
                            "volume",
                            [DEF(INTEGER, name="volume", required=True, gen="make_audio_volume")],
                        ),
                        DEF(
                            "noise-reduction",
                            [
                                DEF(
                                    "admin-status",
                                    [
                                        DEF(
                                            BOOL,
                                            required=True,
                                            name="admin_status",
                                            gen="make_audio_noise_reduction_admin_status",
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
            name="name",
            multi=True,
        )
    ],
)
