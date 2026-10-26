# ----------------------------------------------------------------------
# Managed Object Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile as ManagedObjectProfileModel

from ..models.managedobjectprofile import ManagedObjectProfile
from .base import BaseLoader


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "managedobjectprofile"
    model = ManagedObjectProfileModel
    data_model = ManagedObjectProfile
