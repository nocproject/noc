# ----------------------------------------------------------------------
# ConfDB media streams <name> overlays syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ....defs import DEF
from ....patterns import ANY, BOOL, INTEGER

MEDIA_STREAMS_OVERLAYS_SYNTAX = DEF(
    "overlays",
    [
        DEF(
            ANY,
            [
                DEF(
                    "admin-status",
                    [
                        DEF(
                            BOOL,
                            name="admin_status",
                            required=True,
                            gen="make_media_streams_overlay_status",
                        )
                    ],
                ),
                DEF(
                    "position",
                    [
                        DEF(
                            "x",
                            [
                                DEF(
                                    INTEGER,
                                    name="x",
                                    required=True,
                                    gen="make_media_streams_overlay_position_x",
                                )
                            ],
                        ),
                        DEF(
                            "y",
                            [
                                DEF(
                                    INTEGER,
                                    name="y",
                                    required=True,
                                    gen="make_media_streams_overlay_position_y",
                                )
                            ],
                        ),
                    ],
                ),
                DEF(
                    "text",
                    [DEF(ANY, name="text", required=True, gen="make_media_streams_overlay_text")],
                ),
            ],
            name="overlay_name",
        )
    ],
)
