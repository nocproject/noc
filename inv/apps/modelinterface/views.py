# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.modelinterface application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.modelinterface import ModelInterface
from noc.main.models.collectioncache import CollectionCache


class ModelInterfaceApplication(ExtDocApplication):
    """
    ModelInterface application
    """
    title = "Model Interface"
    menu = "Setup | Model Interfaces"
    model = ModelInterface
    query_fields = ["name__icontains", "description__icontains"]

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        mi = self.get_object_or_404(ModelInterface, id=id)
        return mi.to_json()
