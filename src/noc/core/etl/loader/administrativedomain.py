# ----------------------------------------------------------------------
# Administrative Domain loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainModel

from ..models.administrativedomain import AdministrativeDomain
from .base import BaseLoader


class AdminitstrativeDomainLoader(BaseLoader):
    """
    Administrative Domain loader
    """

    name = "administrativedomain"
    model = AdministrativeDomainModel
    data_model = AdministrativeDomain
