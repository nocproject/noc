# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Mappings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ReferenceField, DictField, DateTimeField
## NOC modules
from noc.main.models.pool import Pool
from noc.core.service.event import fire
from noc.sa.models.objectstatus import ObjectStatus


logger = logging.getLogger(__name__)


class ObjectMap(Document):
    meta = {
        "collection": "noc.cache.object_map"
    }

    # Pool
    pool = ReferenceField(Pool, unique=True)
    # Syslog source ip -> object id
    syslog_sources = DictField()
    # Trap source ip -> object id
    trap_sources = DictField()
    #
    ping_sources = DictField()
    #
    updated = DateTimeField()

    TTL = 600

    def __unicode__(self):
        return self.pool.name

    @classmethod
    def rebuild_pool(cls, pool):
        def aq(s):
            return s.replace(".", "_")

        from noc.sa.models.managedobject import ManagedObject
        logger.info("Updating object mappings for pool %s", pool.name)
        syslog_sources = {}
        trap_sources = {}
        ping_sources = {}
        for mo in ManagedObject.objects.filter(
            pool=pool
        ).exclude(
            trap_source_type="d", syslog_source_type="d"
        ).only("id", "name", "address",
               "trap_source_type", "syslog_source_type",
               "trap_source_ip", "syslog_source_ip"):
            # Process trap sources
            if mo.trap_source_type == "m":
                trap_sources[aq(mo.address)] = mo.id
            elif mo.trap_source_type == "s" and mo.trap_source_ip:
                trap_sources[aq(mo.trap_source_ip)] = mo.id
            elif mo.trap_source_type == "d":
                pass
            else:
                logger.info(
                    "Cannot generate trap source mapping for %s",
                    mo.name
                )
            # Process syslog sources
            if mo.syslog_source_type == "m":
                syslog_sources[aq(mo.address)] = mo.id
            elif mo.syslog_source_type == "s" and mo.syslog_source_ip:
                syslog_sources[aq(mo.syslog_source_ip)] = mo.id
            elif mo.syslog_source_type == "d":
                pass
            else:
                logger.info(
                    "Cannot generate syslog source mapping for %s",
                    mo.name
                )
        # Get ping settings
        for mo in ManagedObject.objects.filter(
            pool=pool,
            object_profile__enable_ping=True
        ).select_related(
            "object_profile"
        ).only("id", "address", "object_profile",
               "object_profile__ping_interval"
        ):
            if mo.object_profile.ping_interval and mo.object_profile.ping_interval > 0:
                ping_sources[aq(mo.address)] = {
                    "id": mo.id,
                    "interval": mo.object_profile.ping_interval,
                    "status": True
                }
        # Resolve object statuses
        oids = dict((d["id"], q) for q, d in ping_sources.iteritems())
        for o in [x for x, y in ObjectStatus.get_statuses(list(oids)).iteritems() if not y]:
            ping_sources[oids[o]]["status"] = False
        # Update mappings
        ObjectMap._get_collection().update({
            "pool": pool.id
        }, {
            "$set": {
                "pool": pool.id,
                "syslog_sources": syslog_sources,
                "trap_sources": trap_sources,
                "ping_sources": ping_sources,
                "updated": datetime.datetime.now()
            }
        }, upsert=True)

    @classmethod
    def get_object_mappings(cls, pool):
        """
        Returns object mappings for pool. Regenerate when necessary
        """
        om = cls._get_collection().find_one({
            "pool": pool.id
        })
        if not om or om["updated"] < datetime.datetime.now() - datetime.timedelta(seconds=cls.TTL):
            cls.rebuild_pool(pool)
            om = cls._get_collection().find_one({
                "pool": pool.id
            })
        return om

    @classmethod
    def get_syslog_sources(cls, pool):
        """
        Returns a dict of IP -> object id for syslog sources
        """
        om = cls.get_object_mappings(pool)
        return dict((k.replace("_", "."), om["syslog_sources"][k])
                    for k in om["syslog_sources"])

    @classmethod
    def get_trap_sources(cls, pool):
        """
        Returns a dict of IP -> object id for trap sources
        """
        om = cls.get_object_mappings(pool)
        return dict((k.replace("_", "."), om["trap_sources"][k])
                    for k in om["trap_sources"])

    @classmethod
    def get_ping_sources(cls, pool):
        """
        Returns a dict of IP -> {"id": ..., "status": ..., "interval": ...}
        """
        om = cls.get_object_mappings(pool)
        return dict((k.replace("_", "."), om["ping_sources"][k])
                    for k in om["ping_sources"])

    @classmethod
    def invalidate(cls, pool):
        """
        Invalidate pool mappings
        """
        logger.debug("Invalidating object mappings for %s", pool)
        ObjectMap._get_collection().update({
            "pool": pool.id
        }, {
            "$set": {
                "updated": datetime.datetime.now() - datetime.timedelta(seconds=cls.TTL)
            }
        })
        fire("objmapchange-%s" % pool)
