# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# crm.subscriber application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.crm.models.subscriber import Subscriber
from noc.lib.app.decorators.state import state_handler
from noc.core.translation import ugettext as _


@state_handler
class SubscriberApplication(ExtDocApplication):
    """
    Subscriber application
    """
    title = _("Subscriber")
    menu = _("Subscribers")
    model = Subscriber
    query_fields = ["name__icontains"]

    def field_row_class(self, o):
        if o.profile and o.profile.style:
            return o.profile.style.css_class_name
        return ""
