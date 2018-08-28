# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseLoader
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """
    name = "managedobjectprofile"
    model = ManagedObjectProfile
    fields = [
        "id",
        "name",
        "level"
    ]
