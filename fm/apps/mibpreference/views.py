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

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        p = self.get_object_or_404(MIBPreference, id=id)
        return p.to_json()
