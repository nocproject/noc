# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.mibpreference application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication
from noc.fm.models import MIBPreference


class MIBPreferenceApplication(ExtDocApplication):
    """
    MIBPreference application
    """
    title = "MIB Preference"
    menu = "Setup | MIB Preference"
    model = MIBPreference
