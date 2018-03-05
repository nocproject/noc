# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ServiceProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from base import BaseLoader
from noc.sa.models.serviceprofile import ServiceProfile


class ServiceProfileLoader(BaseLoader):
    """
    Service Profile loader
    """
    name = "serviceprofile"
    model = ServiceProfile
    fields = [
        "id",
        "name",
        "description",
        "card_title_template"
    ]
