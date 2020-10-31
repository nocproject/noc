# ----------------------------------------------------------------------
# ServiceProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.serviceprofile import ServiceProfile
from noc.sa.models.serviceprofile import ServiceProfile as ServiceProfileModel


class ServiceProfileLoader(BaseLoader):
    """
    Service Profile loader
    """

    name = "serviceprofile"
    model = ServiceProfileModel
    data_model = ServiceProfile
