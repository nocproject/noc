# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Caching engine
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.settings import config
from noc.lib.cache import Cache
from noc.sa.models import ManagedObjectSelector


class ManagedObjectSelectorObjectsIds(Cache):
    """
    Managed Object's selector -> list of object ids
    """
    cache_id = "sa_managedobjectselector_object_ids"
    ttl = config.getint("cache", "sa_managedobjectselector_object_ids")

    @classmethod
    def get_key(cls, selector):
        if hasattr(selector, "id"):
            return selector.id
        else:
            return int(selector)

    @classmethod
    def find(cls, selector):
        if not hasattr(selector, "id"):
            selector = ManagedObjectSelector.objects.get(id=int(selector))
        return set(selector.managed_objects.values_list("id", flat=True))


# Instances
managedobjectselector_object_ids = ManagedObjectSelectorObjectsIds()
