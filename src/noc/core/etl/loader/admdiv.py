# ----------------------------------------------------------------------
# Administrative division loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.gis.models.division import Division

from ..models.admdiv import AdmDiv
from .base import BaseLoader


class AdmDivLoader(BaseLoader):
    """
    Administrative division loader
    """

    name = "admdiv"
    model = Division
    data_model = AdmDiv
