# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB media streams <name> video syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import BOOL, INTEGER, CHOICES

MEDIA_STREAMS_VIDEO_SYNTAX = DEF(
    "video",
    [
        DEF(
            "admin-status",
            [
                DEF(
                    BOOL,
                    name="admin_status",
                    required=True,
                    gen="make_media_streams_video_admin_status",
                )
            ],
        ),
        DEF(
            "resolution",
            [
                DEF(
                    "width",
                    [
                        DEF(
                            INTEGER,
                            name="width",
                            required=True,
                            gen="make_media_streams_video_resolution_width",
                        )
                    ],
                ),
                DEF(
                    "height",
                    [
                        DEF(
                            INTEGER,
                            name="height",
                            required=True,
                            gen="make_media_streams_video_resolution_height",
                        )
                    ],
                ),
            ],
        ),
        DEF(
            "codec",
            [
                DEF("mpeg4", []),
                DEF(
                    "h264",
                    [
                        DEF(
                            "profile",
                            [
                                DEF(
                                    "name",
                                    [
                                        DEF(
                                            CHOICES("cbp", "bp", "mp", "hip", "phip", "chip"),
                                            name="profile",
                                            required=True,
                                            gen="make_media_streams_video_codec_h264_profile_name",
                                        )
                                    ],
                                ),
                                DEF(
                                    "id",
                                    [
                                        DEF(
                                            INTEGER,
                                            name="id",
                                            required=True,
                                            gen="make_media_streams_video_codec_h264_profile_id",
                                        )
                                    ],
                                ),
                                DEF(
                                    "constraint-set",
                                    [
                                        DEF(
                                            INTEGER,
                                            name="constraints",
                                            required=True,
                                            gen="make_media_streams_video_codec_h264_profile_constrains",
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                    gen="make_media_streams_video_codec_h264",
                ),
            ],
        ),
    ],
)
