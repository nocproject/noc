# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ConfDB media streams <name> audio syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from ....defs import DEF
from ....patterns import ANY, BOOL

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
        )
    ],
)
