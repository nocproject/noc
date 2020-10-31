# ----------------------------------------------------------------------
# Managed Object Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile as ManagedObjectProfileModel
from noc.sa.models.capsprofile import CapsProfile


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "managedobjectprofile"
    model = ManagedObjectProfileModel
    data_model = ManagedObjectProfile
