# ---------------------------------------------------------------------
# crm.subscriber application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.crm.models.subscriber import Subscriber
from noc.services.web.base.decorators.state import state_handler
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
    implied_permissions = {"read": ["project:project:lookup"]}
