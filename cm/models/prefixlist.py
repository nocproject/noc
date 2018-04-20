# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Prefix-List Object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import datetime
import os
# NOC modules
from .object import Object
=======
##----------------------------------------------------------------------
## Prefix-List Object
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
import os
## NOC modules
from object import Object
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

logger = logging.getLogger(__name__)


class PrefixList(Object):
<<<<<<< HEAD
    class Meta(object):
=======
    class Meta:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        app_label = "cm"
        db_table = "cm_prefixlist"
        verbose_name = "Prefix List"
        verbose_name_plural = "Prefix Lists"

    repo_name = "prefix-list"

    @classmethod
    def build_prefix_lists(cls):
<<<<<<< HEAD
        from noc.peer.models.peeringpoint import PeeringPoint
        from noc.peer.models.whoiscache import WhoisCache
=======
        from noc.peer.models import PeeringPoint, WhoisCache
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        for pp in PeeringPoint.objects.all():
            profile = pp.profile
            for name, filter_exp in pp.generated_prefix_lists:
                prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(filter_exp)
                pl = profile.generate_prefix_list(name, prefixes)
                yield (pp, name, pl, prefixes)

    @classmethod
    def global_pull(cls):
<<<<<<< HEAD
        from noc.peer.models.prefixlistcache import PrefixListCache, PrefixListCachePrefix
=======
        from noc.peer.models import PrefixListCache, PrefixListCachePrefix
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        objects = {}
        for o in PrefixList.objects.all():
            objects[o.repo_path] = o
        c_objects = set()  # peering_point/name
        logger.debug("PrefixList.global_pull(): building prefix lists")
        for peering_point, pl_name, pl, prefixes in cls.build_prefix_lists():
            logger.debug(
                "PrefixList.global_pull(): writing %s/%s (%d lines)" % (
<<<<<<< HEAD
                    peering_point.hostname, pl_name, len(pl.split("\n"))
                )
            )
=======
                peering_point.hostname, pl_name, len(pl.split("\n"))))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            path = os.path.join(peering_point.hostname, pl_name)
            if path in objects:
                o = objects[path]
                del objects[path]
            else:
                o = PrefixList(repo_path=path)
                o.save()
            o.write(pl)
            # Populate cache
            cname = "%s/%s" % (peering_point.hostname, pl_name)
            try:
                c = PrefixListCache.objects.get(peering_point=peering_point.id,
                                                name=pl_name)
                if c.cmp_prefixes(prefixes):
                    logger.debug("Updating cache for %s" % cname)
                    c.changed = datetime.datetime.now()
                    c.prefixes = [PrefixListCachePrefix(prefix=prefix,
                                                        min=min, max=max)
                                  for prefix, min, max in prefixes]
                    c.save()
            except PrefixListCache.DoesNotExist:
                logger.debug("Writing cache for %s" % cname)
                PrefixListCache(peering_point=peering_point.id,
                                name=pl_name,
                                prefixes=[PrefixListCachePrefix(prefix=prefix,
                                                                min=min,
                                                                max=max)
                                          for prefix, min, max in
                                          prefixes]).save()
            c_objects.add("%s/%s" % (peering_point.hostname, pl_name))
        # Remove deleted prefix lists
        for o in objects.values():
            o.delete()
        # Remove unused cache entries
        for o in PrefixListCache.objects.all():
            n = "%s/%s" % (o.peering_point.hostname, o.name)
            if n not in c_objects:
                o.delete()
