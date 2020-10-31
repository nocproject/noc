# ----------------------------------------------------------------------
# Auth Profile Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.authprofile import AuthProfile
from noc.sa.models.authprofile import AuthProfile as AuthProfileModel


class AuthProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "authprofile"
    model = AuthProfileModel
    data_model = AuthProfile
