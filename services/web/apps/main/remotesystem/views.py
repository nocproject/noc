# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.remotesystem application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app import ExtDocApplication
from noc.main.models.remotesystem import RemoteSystem


class RemoteSystemApplication(ExtDocApplication):
    """
    RemoteSystem application
    """
    title = "Remote System"
    menu = [_("Setup"), _("Remote Systems")]
    model = RemoteSystem
