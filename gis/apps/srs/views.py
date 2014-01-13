# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.srs application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication
from noc.gis.models.srs import SRS


class SRSApplication(ExtModelApplication):
    """
    SRS application
    """
    title = "SRS"
    menu = "Setup | SRS"
    model = SRS
    query_fields = ["auth_name__contains", "proj4text__contains"]
    int_query_fields = ["auth_srid"]
