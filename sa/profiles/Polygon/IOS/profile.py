# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Polygon
# OS:     IOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Polygon.IOS"
    pattern_more = [
        (r"^ --More--", "\n"),
        (r"(?:\?|interfaces)\s*\[confirm\]", "\n")
    ]
