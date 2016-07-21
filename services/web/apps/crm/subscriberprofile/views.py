# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## crm.subscriberprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.core.translation import ugettext as _


class SubscriberProfileApplication(ExtDocApplication):
    """
    SubscriberProfile application
    """
    title = _("Subscriber Profile")
    menu = [_("Setup"), _("Subscriber Profiles")]
    model = SubscriberProfile
    query_fields = ["name__icontains", "description__icontains"]

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
