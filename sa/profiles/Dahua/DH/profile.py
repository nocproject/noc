# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Dahua
# OS:     DH
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Dahua.DH"
    enable_http_session = True
    http_request_middleware = ["digestauth"]

    @staticmethod
    def parse_equal_output(string):
        r = dict(l.split("=", 1) for l in string.splitlines())
        return r
