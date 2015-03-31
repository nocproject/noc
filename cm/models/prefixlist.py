# -*- coding: utf-8 -*-
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

logger = logging.getLogger(__name__)


class PrefixList(Object):
    class Meta:
        app_label = "cm"
        db_table = "cm_prefixlist"
        verbose_name = "Prefix List"
        verbose_name_plural = "Prefix Lists"

    repo_name = "prefix-list"

    @classmethod
    def build_prefix_lists(cls):
        from noc.peer.models import PeeringPoint, WhoisCache

        for pp in PeeringPoint.objects.all():
            profile = pp.profile
            for name, filter_exp in pp.generated_prefix_lists:
                prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(filter_exp)
                pl = profile.generate_prefix_list(name, prefixes)
                yield (pp, name, pl, prefixes)

    @classmethod
    def global_pull(cls):
        from noc.peer.models import PrefixListCache, PrefixListCachePrefix

        objects = {}
        for o in PrefixList.objects.all():
            objects[o.repo_path] = o
        c_objects = set()  # peering_point/name
        logger.debug("PrefixList.global_pull(): building prefix lists")
        for peering_point, pl_name, pl, prefixes in cls.build_prefix_lists():
            logger.debug(
                "PrefixList.global_pull(): writing %s/%s (%d lines)" % (
                peering_point.hostname, pl_name, len(pl.split("\n"))))
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
