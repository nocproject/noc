# ---------------------------------------------------------------------
# Vendor: Audiocodes
# OS:     Mediant2000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Audiocodes.Mediant2000"

    pattern_more = [(rb"^ -- More --", b"\n")]
    http_request_middleware = ["digestauth"]
