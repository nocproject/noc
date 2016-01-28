# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rebuild pop links
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
import logging
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link

logger = logging.getLogger(__name__)


class LinkedPoP(object):
    def __init__(self, pop_id):
        self.pop = Object.objects.filter(id=pop_id).first()

    def iter_db_links(self):
        """
        Yield remote pop, level
        """
        for c, remote, _ in self.pop.get_genderless_connections(
                "links"):
            yield c, remote, c.data["level"]

    def get_pop_objects(self, root=None):
        """
        Get managed objects inside PoP
        """
        if not root:
            root = self.pop
        mos = set()
        for o in root.get_content():
            if o.get_data("management", "managed"):
                # Managed object
                mo = o.get_data("management", "managed_object")
                if mo:
                    mos.add(mo)
            if o.get_data("container", "container"):
                mos |= self.get_pop_objects(o)
        return mos

    def get_linked_pops(self):
        linked = set()
        self.pops = set(self.get_pop_objects())
        self_interfaces = set(
                i.id for i in Interface.objects.filter(
                        managed_object__in=self.pops)
        )
        for l in Link.objects.filter(interfaces__in=self_interfaces):
            ri = (i for i in l.interfaces
                  if i.id not in self_interfaces)
            if ri:
                # Remote link
                ro = set()
                for i in ri:
                    ro.add(i.managed_object.id)
                if len(ro) == 1 and ro:
                    for o in Object.get_managed(ro.pop()):
                        pop = o.get_pop()
                        if pop and pop not in linked:
                            linked.add(pop)
        return linked

    def update_links(self):
        if not self.pop:
            return
        level = self.pop.get_data("pop", "level")
        linked = self.get_linked_pops()
        for c, pop, l_level in self.iter_db_links():
            r_level = min(level, l_level)
            if pop in linked:
                # Already linked
                if r_level != l_level:
                    # Adjust link level
                    logger.info(
                        "%s - %s. Changing link level to %d",
                        self.pop, pop, r_level
                    )
                    c.data["level"] = r_level
                    c.save()
                linked.remove(pop)
            else:
                # Unlink
                logger.info("Unlinking %s - %s", self.pop, pop)
                c.delete()
        # New links
        for pop in linked:
            r_level = min(level, pop.get_data("pop", "level"))
            logger.info(
                "%s - %s. Linking with level %d",
                self.pop, pop, r_level
            )
            self.pop.connect_genderless(
                "links", pop, "links",
                {"level": r_level}, type="pop_link"
            )


def update_pop_links(pop_id):
    """
    Handler for delayed call
    """
    LinkedPoP(pop_id).update_links()
