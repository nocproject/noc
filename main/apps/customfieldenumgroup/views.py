# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.customfieldenumgroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.main.models import CustomFieldEnumGroup, CustomFieldEnumValue


class CustomFieldEnumGroupApplication(ExtModelApplication):
    """
    CustomFieldEnumGroup application
    """
    title = "Enum Groups"
    menu = "Setup | Enum Groups"
    model = CustomFieldEnumGroup

    values = ModelInline(CustomFieldEnumValue)
