# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.mibpreference application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.fm.models.mibpreference import MIBPreference
from noc.core.translation import ugettext as _


class MIBPreferenceApplication(ExtDocApplication):
    """
    MIBPreference application
    """
    title = _("MIB Preference")
    menu = [_("Setup"), _("MIB Preference")]
    model = MIBPreference
