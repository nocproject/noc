# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Auth Profile Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from base import BaseLoader
from noc.sa.models.authprofile import AuthProfile


class AuthProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """
    name = "authprofile"
    model = AuthProfile
    fields = [
        "id",
        "name",
        "description",
        "type",
        "user",
        "password",
        "super_password",
        "snmp_ro",
        "snmp_rw"
    ]
