# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Language Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext as _
## NOC modules
from noc.lib.app import ExtModelApplication
from noc.main.models import Language


class LanguageApplication(ExtModelApplication):
    title = _("Languages")
    model = Language
    menu = "Setup | Languages"
    query_fields = ["name__icontains", "native_name__icontains"]
