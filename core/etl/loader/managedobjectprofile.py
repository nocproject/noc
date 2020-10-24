# ----------------------------------------------------------------------
# Managed Object Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.managedobjectprofile import ManagedObjectProfileModel
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.capsprofile import CapsProfile


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "managedobjectprofile"
    model = ManagedObjectProfile
    data_model = ManagedObjectProfileModel
    fields = ["id", "name", "level"]

    def clean(self, row):
        """
        Fix pool
        """
        v = super().clean(row)
        v["caps_profile"] = CapsProfile.objects.filter(name="default").first()
        return v
