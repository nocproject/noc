# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.service application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.service import Service
from noc.core.translation import ugettext as _
from noc.lib.validators import is_objectid


class ServiceApplication(ExtDocApplication):
    """
    Service application
    """
    title = "Services"
    menu = [_("Services")]
    model = Service
    parent_model = Service
    parent_field = "parent"
    query_fields = ["id"]

    def get_Q(self, request, query):
        if is_objectid(query):
            q = Q(id=query)
        else:
            q = super(ServiceApplication, self).get_Q(request, query)
        return q
