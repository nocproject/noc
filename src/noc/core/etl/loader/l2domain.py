# ----------------------------------------------------------------------
# Auth Profile Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.vc.models.l2domain import L2Domain as L2DomainModel

from ..models.l2domain import L2Domain
from .base import BaseLoader


class L2DomainLoader(BaseLoader):
    """
    L2Domain loader
    """

    name = "l2domain"
    model = L2DomainModel
    data_model = L2Domain
