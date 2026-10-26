# ----------------------------------------------------------------------
# Auth Profile Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.authprofile import AuthProfile as AuthProfileModel

from ..models.authprofile import AuthProfile
from .base import BaseLoader


class AuthProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "authprofile"
    model = AuthProfileModel
    data_model = AuthProfile
