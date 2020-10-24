# ----------------------------------------------------------------------
# Administrative Domain loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.administrativedomain import AdministrativeDomainModel
from noc.sa.models.administrativedomain import AdministrativeDomain


class AdminitstrativeDomainLoader(BaseLoader):
    """
    Administrative Domain loader
    """

    name = "administrativedomain"
    model = AdministrativeDomain
    data_model = AdministrativeDomainModel
    fields = ["id", "name", "parent", "default_pool"]
    mapped_fields = {"parent": "administrativedomain"}
