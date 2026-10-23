# ---------------------------------------------------------------------
# Vendor: Ubiquiti
# OS:     Controller
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ubiquiti.Ubiquiti"

    http_request_middleware = [
        "noc.sa.profiles.Ubiquiti.Controller.middleware.ubiquityauth.UbiquitiAuthMiddeware",
    ]
