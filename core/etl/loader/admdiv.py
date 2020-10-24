# ----------------------------------------------------------------------
# Administrative division loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.admdiv import AdmDivModel
from noc.gis.models.division import Division


class AdmDivLoader(BaseLoader):
    """
    Administrative division loader
    """

    name = "admdiv"
    model = Division
    data_model = AdmDivModel
    fields = ["id", "parent", "name", "short_name"]

    mapped_fields = {"parent": "admdiv"}
