# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIMEType Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext as _
## NOC modules
from noc.lib.app import ExtModelApplication
from noc.main.models import MIMEType


class MIMETypeApplication(ExtModelApplication):
    title = _("MIME Types")
    model = MIMEType
    menu = "Setup | MIME Types"
