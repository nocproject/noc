# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Administrative division loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.gis.models.division import Division


class AdmDivLoader(BaseLoader):
    """
    Administrative division loader
    """
    name = "admdiv"
    model = Division
    fields = [
        "id",
        "parent",
        "name",
        "short_name"
    ]

    mapped_fields = {
        "parent": "admdiv"
    }
