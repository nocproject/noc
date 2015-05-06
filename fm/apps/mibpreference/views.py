# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.mibpreference application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import MIBPreference
from noc.main.models.collectioncache import CollectionCache


class MIBPreferenceApplication(ExtDocApplication):
    """
    MIBPreference application
    """
    title = "MIB Preference"
    menu = "Setup | MIB Preference"
    model = MIBPreference

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))
