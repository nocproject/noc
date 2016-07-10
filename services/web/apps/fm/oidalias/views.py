# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.oidalias application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import OIDAlias
from noc.main.models.collectioncache import CollectionCache


class OIDAliasApplication(ExtDocApplication):
    """
    OIDAlias application
    """
    title = "OID Aliases"
    menu = "Setup | OID Aliases"
    model = OIDAlias

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        oa = self.get_object_or_404(OIDAlias, id=id)
        return oa.to_json()
