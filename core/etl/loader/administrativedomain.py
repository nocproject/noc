# ----------------------------------------------------------------------
# Administrative Domain loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.administrativedomain import AdministrativeDomain
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainModel


class AdminitstrativeDomainLoader(BaseLoader):
    """
    Administrative Domain loader
    """

    name = "administrativedomain"
    model = AdministrativeDomainModel
    data_model = AdministrativeDomain
