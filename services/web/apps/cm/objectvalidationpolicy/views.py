# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.objectvalidationpolicy application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.cm.models.objectvalidationpolicy import ObjectValidationPolicy
from noc.core.translation import ugettext as _


class ObjectValidationPolicyApplication(ExtDocApplication):
    """
    ObjectValidationPolicy application
    """

    title = "Object Validation Policy"
    menu = [_("Setup"), _("Object Validation Policies")]
    model = ObjectValidationPolicy
