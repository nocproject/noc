# ---------------------------------------------------------------------
# sa.serviceinstance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.serviceinstance import ServiceInstance
from noc.core.translation import ugettext as _


class ServiceInstanceApplication(ExtDocApplication):
    """
    sa.serviceinstance application
    """

    title = _("Service Instances")
    menu = _("Service Instances")
    model = ServiceInstance
    query_fields = ["name__contains"]
