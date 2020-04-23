# ----------------------------------------------------------------------
# Managed Object Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.capsprofile import CapsProfile


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "managedobjectprofile"
    model = ManagedObjectProfile
    fields = ["id", "name", "level"]

    def clean(self, row):
        """
        Fix pool
        """
        v = super(ManagedObjectProfileLoader, self).clean(row)
        v["caps_profile"] = CapsProfile.objects.filter(name="default").first()
        return v
