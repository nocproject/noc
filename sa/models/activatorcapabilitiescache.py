# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ActivatorCapabilitiesCache
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.main.models import Shard
from noc.lib.nosql import Document, IntField


class ActivatorCapabilitiesCache(Document):
    meta = {
        "collection": "noc.activatorcapscache",
        "allow_inheritance": False
    }

    activator_id = IntField()
    members = IntField()
    max_scripts = IntField()

    def __unicode__(self):
        return u"Activator Caps (%d)" % self.activator_id

    @classmethod
    def reset_cache(cls, shards):
        """
        Reset caches for shards
        :param shard: List of shard names or ids
        """
        ids = []
        for shard in shards:
            if isinstance(shard, basestring):
                s = Shard.objects.get(name=shard)
            else:
                s = Shard.objects.get(pk=shard)
            ids += s.activator_set.values_list("id", flat=True)
        ActivatorCapabilitiesCache.objects(activator_id__in=ids).delete()

    @property
    def activator(self):
        if not hasattr(self, "_activator"):
            from activator import Activator
            self._activator = Activator.objects.get(id=self.activator_id)
        return self._activator
