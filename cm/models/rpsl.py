# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RPSL Object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import logging
# NOC modules
from .object import Object

logger = logging.getLogger(__name__)


class RPSL(Object):
    class Meta(object):
        app_label = "cm"
        db_table = "cm_rpsl"
        verbose_name = "RPSL Object"
        verbose_name_plural = "RPSL Objects"

    repo_name = "rpsl"

    @classmethod
    def global_pull(cls):
        def global_pull_class(name, c, name_fun):
            objects = {}
            for o in RPSL.objects.filter(
                    repo_path__startswith=name + os.sep):
                objects[o.repo_path] = o
            for a in c.objects.all():
                if not a.rpsl:
                    continue
                path = os.path.join(name, name_fun(a))
                if path in objects:
                    o = objects[path]
                    del objects[path]
                else:
                    o = RPSL(repo_path=path)
                    o.save()
                o.write(a.rpsl)
            for o in objects.values():
                o.delete()

        from noc.peer.models.asn import AS
        from noc.peer.models.asset import ASSet
        from noc.peer.models.peeringpoint import PeeringPoint
        from noc.dns.models.dnszone import DNSZone

        logger.debug("RPSL.global_pull(): building RPSL")
        global_pull_class("inet-rtr", PeeringPoint,
                          lambda a: a.hostname)
        global_pull_class("as", AS, lambda a: "AS%d" % a.asn)
        global_pull_class("as-set", ASSet, lambda a: a.name)
        global_pull_class("domain", DNSZone, lambda a: a.name)

    @classmethod
    def global_push(cls):
        pass
