# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.mibpreference application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.mibpreference import MIBPreference
from noc.main.models.collectioncache import CollectionCache
from noc.core.translation import ugettext as _


class MIBPreferenceApplication(ExtDocApplication):
    """
    MIBPreference application
    """
    title = _("MIB Preference")
    menu = [_("Setup"), _("MIB Preference")]
    model = MIBPreference

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))
