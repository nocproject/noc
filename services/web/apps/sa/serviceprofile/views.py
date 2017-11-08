# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.serviceprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.serviceprofile import ServiceProfile


class ServiceProfileApplication(ExtDocApplication):
    """
    ServiceProfile application
    """
    title = _("Service Profile")
    menu = [_("Setup"), _("Service Profiles")]
    model = ServiceProfile
